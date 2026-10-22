"""Google OR-Tools solver: Vehicle Routing Problem with Time Windows (VRPTW).

Handles together:
  * vehicle capacity            (Capacity dimension, hard)
  * delivery time windows       (Time dimension; early arrival waits, late is penalised)
  * priorities                  (late penalty is multiplied for high / urgent orders)
  * workload balance            (span cost on a Count dimension)
  * manual reassignment         (order locked to one vehicle)
  * impossible orders           (disjunction penalty -> left unassigned as last resort)
"""
import time
from typing import Dict, List

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from .evaluate import build_route, compute_metrics, effective_window
from .geo import km_to_min
from .models import Agent, Order, Solution
from .objective import PRIORITY_MULT, W_BAL, W_DIST, W_DROP, W_LATE

SCALE = 100          # OR-Tools needs integer costs
HORIZON = 24 * 60    # minutes


def solve_ortools(agents: List[Agent], orders: List[Order], dist, idx: Dict[str, int],
                  time_limit: int = 3) -> Solution:
    t0 = time.time()
    active = [a for a in agents if a.available]
    omap = {o.id: o for o in orders}

    if not active or not orders:
        routes = [build_route(a.id, [], omap, idx, dist) for a in active]
        unassigned = [o.id for o in orders] if not active else []
        metrics = compute_metrics(routes, unassigned, omap, [a.id for a in active])
        return Solution(method="ortools", routes=routes, unassigned=unassigned, metrics=metrics)

    # node 0 = depot, node i+1 = orders[i]  (matches `idx` built by the caller)
    n_nodes = len(orders) + 1
    node_order: List[Order] = [None] + list(orders)  # type: ignore

    manager = pywrapcp.RoutingIndexManager(n_nodes, len(active), 0)
    routing = pywrapcp.RoutingModel(manager)

    # --- cost: distance ---
    def dist_cb(i, j):
        a, b = manager.IndexToNode(i), manager.IndexToNode(j)
        return int(round(W_DIST * dist[a][b] * SCALE))
    dist_idx = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(dist_idx)

    # --- capacity ---
    def demand_cb(i):
        n = manager.IndexToNode(i)
        return 0 if n == 0 else node_order[n].demand
    demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(demand_idx, 0, [a.capacity for a in active], True, "Capacity")

    # --- time (travel + service), waiting allowed ---
    def time_cb(i, j):
        a, b = manager.IndexToNode(i), manager.IndexToNode(j)
        service = 0 if a == 0 else node_order[a].service_time
        return int(round(km_to_min(dist[a][b]))) + service
    time_idx = routing.RegisterTransitCallback(time_cb)
    routing.AddDimension(time_idx, 180, HORIZON, True, "Time")
    time_dim = routing.GetDimensionOrDie("Time")

    for n in range(1, n_nodes):
        o = node_order[n]
        start, end = effective_window(o)
        index = manager.NodeToIndex(n)
        time_dim.CumulVar(index).SetRange(int(start), HORIZON)
        coef = int(round(W_LATE * PRIORITY_MULT.get(o.priority, 1.0) * SCALE))
        time_dim.SetCumulVarSoftUpperBound(index, int(end), coef)
        # leave order unassigned only as a last resort
        routing.AddDisjunction([index], int(W_DROP * SCALE))
        if o.locked_agent:
            ids = [a.id for a in active]
            if o.locked_agent in ids:
                routing.SetAllowedVehiclesForIndex([ids.index(o.locked_agent)], index)

    # --- workload balance via count dimension ---
    def count_cb(i):
        return 0 if manager.IndexToNode(i) == 0 else 1
    count_idx = routing.RegisterUnaryTransitCallback(count_cb)
    routing.AddDimension(count_idx, 0, len(orders) + 1, True, "Count")
    count_dim = routing.GetDimensionOrDie("Count")
    count_dim.SetGlobalSpanCostCoefficient(int(W_BAL * SCALE * 3))

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = time_limit

    sol = routing.SolveWithParameters(params)
    if sol is None:
        raise RuntimeError("OR-Tools found no solution")

    seqs: Dict[str, List[str]] = {}
    served = set()
    for v, a in enumerate(active):
        seq: List[str] = []
        index = routing.Start(v)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:
                seq.append(node_order[node].id)
                served.add(node_order[node].id)
            index = sol.Value(routing.NextVar(index))
        seqs[a.id] = seq

    unassigned = [o.id for o in orders if o.id not in served]
    routes = [build_route(a.id, seqs[a.id], omap, idx, dist) for a in active]
    metrics = compute_metrics(routes, unassigned, omap, [a.id for a in active])
    return Solution(method="ortools", routes=routes, unassigned=unassigned, metrics=metrics,
                    solve_ms=round((time.time() - t0) * 1000, 1))
