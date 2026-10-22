"""Engine: holds the live state and re-optimizes whenever something changes."""
import copy
import itertools
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

from .baseline import solve_baseline
from .geo import distance_matrix_km
from .models import Agent, Order, Scenario, Solution
from .sample_data import sample_scenario
from .solver_heuristic import solve_heuristic

try:  # OR-Tools is optional: we fall back to the pure-Python optimizer.
    from .solver_ortools import solve_ortools
    HAS_ORTOOLS = True
except Exception:  # pragma: no cover
    solve_ortools = None
    HAS_ORTOOLS = False

SOLVER_PREF = os.environ.get("SOLVER", "auto")  # auto | ortools | heuristic


class Engine:
    def __init__(self):
        self._matrix_cache: Dict[tuple, tuple] = {}
        self._counter = itertools.count(1)
        self.reset()

    # ------------------------------------------------------------------ state
    def reset(self):
        self.scenario: Scenario = sample_scenario()
        self.log: List[dict] = []
        self.optimized: Optional[Solution] = None
        self.baseline: Optional[Solution] = None
        self.matrix_source = "haversine"
        self._next_order = len(self.scenario.orders) + 1
        self.optimize(event_type="init", description="Initial plan for today's shift")
        return self.snapshot()

    def _active_orders(self) -> List[Order]:
        return [o for o in self.scenario.orders if o.status != "cancelled"]

    def _matrix(self, orders: List[Order]):
        pts = [(self.scenario.depot.lat, self.scenario.depot.lng)] + [(o.lat, o.lng) for o in orders]
        key = tuple(pts)
        if key not in self._matrix_cache:
            if len(self._matrix_cache) > 50:
                self._matrix_cache.clear()
            self._matrix_cache[key] = distance_matrix_km(pts)
        dist, src = self._matrix_cache[key]
        self.matrix_source = src
        return dist, {o.id: i + 1 for i, o in enumerate(orders)}

    # --------------------------------------------------------------- optimize
    def _solve(self, orders, dist, idx) -> Solution:
        agents = self.scenario.agents
        if SOLVER_PREF != "heuristic" and HAS_ORTOOLS:
            try:
                return solve_ortools(agents, orders, dist, idx)
            except Exception:
                if SOLVER_PREF == "ortools":
                    raise
        return solve_heuristic(agents, orders, dist, idx)

    def optimize(self, event_type: str, description: str):
        t0 = time.time()
        before = self.optimized
        orders = self._active_orders()
        dist, idx = self._matrix(orders)
        new = self._solve(orders, dist, idx)
        base = solve_baseline(self.scenario.agents, orders, dist, idx)

        moved = 0
        if before:
            old_owner = {s.order_id: r.agent_id for r in before.routes for s in r.stops}
            new_owner = {s.order_id: r.agent_id for r in new.routes for s in r.stops}
            moved = sum(1 for k, v in new_owner.items() if k in old_owner and old_owner[k] != v)

        self.optimized, self.baseline = new, base
        self.log.insert(0, {
            "id": next(self._counter),
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": event_type,
            "description": description,
            "reoptimize_ms": round((time.time() - t0) * 1000, 1),
            "solver": new.method,
            "orders_moved": moved,
            "before": before.metrics.model_dump() if before else None,
            "after": new.metrics.model_dump(),
        })

    # ----------------------------------------------------------------- events
    def _find(self, order_id: str) -> Order:
        for o in self.scenario.orders:
            if o.id == order_id:
                return o
        raise KeyError(f"Order {order_id} not found")

    def add_order(self, name: str, lat: float, lng: float, demand: int = 1, priority: int = 1,
                  tw_start: int = 0, tw_end: int = 240) -> Order:
        oid = f"O{self._next_order}"
        self._next_order += 1
        o = Order(id=oid, name=name or oid, lat=lat, lng=lng, demand=demand, priority=priority,
                  tw_start=tw_start, tw_end=max(tw_end, tw_start))
        self.scenario.orders.append(o)
        self.optimize("add", f"New order {oid} ({o.name}) added, priority {priority}")
        return o

    def cancel_order(self, order_id: str):
        o = self._find(order_id)
        o.status = "cancelled"
        self.optimize("cancel", f"Order {order_id} ({o.name}) cancelled")

    def restore_order(self, order_id: str):
        o = self._find(order_id)
        o.status = "pending"
        o.delay = 0
        self.optimize("restore", f"Order {order_id} ({o.name}) restored")

    def delay_order(self, order_id: str, minutes: int):
        o = self._find(order_id)
        o.delay += minutes
        o.status = "delayed"
        self.optimize("delay", f"Order {order_id} ({o.name}) delayed by {minutes} min")

    def reassign_order(self, order_id: str, agent_id: Optional[str]):
        o = self._find(order_id)
        if agent_id and agent_id not in [a.id for a in self.scenario.agents]:
            raise KeyError(f"Agent {agent_id} not found")
        o.locked_agent = agent_id
        who = agent_id or "any agent (unlocked)"
        self.optimize("reassign", f"Order {order_id} ({o.name}) assigned to {who}")

    def set_agent_available(self, agent_id: str, available: bool):
        agent = next((a for a in self.scenario.agents if a.id == agent_id), None)
        if agent is None:
            raise KeyError(f"Agent {agent_id} not found")
        agent.available = available
        # orders locked to an unavailable agent are released
        if not available:
            for o in self.scenario.orders:
                if o.locked_agent == agent_id:
                    o.locked_agent = None
        state = "back on duty" if available else "off duty (breakdown / leave)"
        self.optimize("agent", f"Agent {agent.name} is {state}")

    # --------------------------------------------------------------- snapshot
    def snapshot(self) -> dict:
        opt, base = self.optimized, self.baseline
        imp = None
        if opt and base:
            bm, om = base.metrics, opt.metrics

            def pct(b, o):
                return round((b - o) / b * 100, 1) if b > 0 else 0.0
            imp = {
                "distance_pct": pct(bm.total_distance_km, om.total_distance_km),
                "late_deliveries_saved": bm.late_deliveries - om.late_deliveries,
                "late_minutes_pct": pct(bm.total_late_minutes, om.total_late_minutes),
                "priority_late_saved": bm.priority_late - om.priority_late,
                "balance_gap_saved": bm.balance_gap - om.balance_gap,
            }
        return {
            "scenario": self.scenario.model_dump(),
            "optimized": opt.model_dump() if opt else None,
            "baseline": base.model_dump() if base else None,
            "improvement": imp,
            "log": self.log[:30],
            "matrix_source": self.matrix_source,
            "solver": opt.method if opt else None,
        }
