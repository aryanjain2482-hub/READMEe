"""Pure-Python optimizer: cheapest insertion + local search.

Needs no extra libraries. Used automatically if Google OR-Tools is not
installed, and also as a safety net if OR-Tools fails.
"""
import time
from typing import Dict, List, Optional

from .evaluate import build_route, compute_metrics
from .models import Agent, Order, Solution
from .objective import W_BAL, W_DROP, route_cost


class _Ctx:
    def __init__(self, agents, orders, dist, idx):
        self.agents = agents
        self.omap: Dict[str, Order] = {o.id: o for o in orders}
        self.dist = dist
        self.idx = idx
        self.cache: Dict[tuple, float] = {}

    def cost(self, agent_id: str, seq: List[str]) -> float:
        key = (agent_id, tuple(seq))
        v = self.cache.get(key)
        if v is None:
            r = build_route(agent_id, seq, self.omap, self.idx, self.dist)
            v = route_cost(r, self.omap)
            if len(self.cache) > 200000:
                self.cache.clear()
            self.cache[key] = v
        return v


def _can_take(a: Agent, seq: List[str], o: Order, omap) -> bool:
    if o.locked_agent and o.locked_agent != a.id:
        return False
    return sum(omap[x].demand for x in seq) + o.demand <= a.capacity


def solve_heuristic(agents: List[Agent], orders: List[Order], dist, idx,
                    time_limit: float = 2.0) -> Solution:
    t0 = time.time()
    active = [a for a in agents if a.available]
    ctx = _Ctx(active, orders, dist, idx)
    omap = ctx.omap
    seqs: Dict[str, List[str]] = {a.id: [] for a in active}
    unassigned: List[str] = []

    # 1) Construction: urgent + early-deadline orders first, cheapest insertion.
    order_list = sorted(orders, key=lambda o: (-o.priority, o.tw_end + o.delay))
    for o in order_list:
        best: Optional[tuple] = None
        for a in active:
            cur = seqs[a.id]
            if not _can_take(a, cur, o, omap):
                continue
            base = ctx.cost(a.id, cur)
            for pos in range(len(cur) + 1):
                cand = cur[:pos] + [o.id] + cur[pos:]
                delta = ctx.cost(a.id, cand) - base + W_BAL * ((len(cur) + 1) ** 2 - len(cur) ** 2)
                if best is None or delta < best[0]:
                    best = (delta, a.id, pos)
        if best is None:
            unassigned.append(o.id)
        else:
            _, aid, pos = best
            seqs[aid].insert(pos, o.id)

    # 2) Improvement: relocate + intra-route reversal until no gain / time out.
    def total() -> float:
        return sum(ctx.cost(a.id, seqs[a.id]) + W_BAL * len(seqs[a.id]) ** 2 for a in active) \
            + W_DROP * len(unassigned)

    improved = True
    while improved and time.time() - t0 < time_limit:
        improved = False
        # relocate one order anywhere
        for a in active:
            for oid in list(seqs[a.id]):
                if time.time() - t0 > time_limit:
                    break
                src = seqs[a.id]
                if oid not in src:
                    continue
                i = src.index(oid)
                src_wo = src[:i] + src[i + 1:]
                src_gain = ctx.cost(a.id, src) - ctx.cost(a.id, src_wo) \
                    + W_BAL * (len(src) ** 2 - len(src_wo) ** 2)
                best = None
                for b in active:
                    base_seq = src_wo if b.id == a.id else seqs[b.id]
                    if b.id != a.id and not _can_take(b, base_seq, omap[oid], omap):
                        continue
                    if b.id != a.id and omap[oid].locked_agent and omap[oid].locked_agent != b.id:
                        continue
                    base = ctx.cost(b.id, base_seq)
                    for pos in range(len(base_seq) + 1):
                        if b.id == a.id and pos == i:
                            continue
                        cand = base_seq[:pos] + [oid] + base_seq[pos:]
                        add = ctx.cost(b.id, cand) - base \
                            + W_BAL * ((len(base_seq) + 1) ** 2 - len(base_seq) ** 2)
                        if b.id == a.id:
                            delta = ctx.cost(a.id, cand) - ctx.cost(a.id, src)
                        else:
                            delta = add - src_gain
                        if delta < -1e-6 and (best is None or delta < best[0]):
                            best = (delta, b.id, pos)
                if best:
                    _, bid, pos = best
                    seqs[a.id].remove(oid)
                    seqs[bid].insert(pos, oid)
                    improved = True
        # intra-route 2-opt style reversal
        for a in active:
            s = seqs[a.id]
            for i in range(len(s) - 1):
                for j in range(i + 1, len(s)):
                    cand = s[:i] + s[i:j + 1][::-1] + s[j + 1:]
                    if ctx.cost(a.id, cand) < ctx.cost(a.id, s) - 1e-6:
                        s = cand
                        seqs[a.id] = s
                        improved = True

    # 3) Try to place anything that was dropped. If every vehicle is "almost full",
    #    move one order to another vehicle to free the space (simple repair step).
    for oid in list(unassigned):
        o = omap[oid]
        placed = False
        for a in active:
            if _can_take(a, seqs[a.id], o, omap):
                seqs[a.id].append(oid)
                placed = True
                break
        if not placed:
            for a in active:
                for x in list(seqs[a.id]):
                    if omap[x].locked_agent == a.id:
                        continue
                    rest = [y for y in seqs[a.id] if y != x]
                    if not _can_take(a, rest, o, omap):
                        continue
                    for b in active:
                        if b.id != a.id and _can_take(b, seqs[b.id], omap[x], omap):
                            seqs[a.id] = rest + [oid]
                            seqs[b.id].append(x)
                            placed = True
                            break
                    if placed:
                        break
                if placed:
                    break
        if placed:
            unassigned.remove(oid)

    routes = [build_route(a.id, seqs[a.id], omap, idx, dist) for a in active]
    metrics = compute_metrics(routes, unassigned, omap, [a.id for a in active])
    return Solution(method="heuristic", routes=routes, unassigned=unassigned, metrics=metrics,
                    solve_ms=round((time.time() - t0) * 1000, 1))
