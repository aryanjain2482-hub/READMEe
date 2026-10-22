"""Shared cost weights so every solver optimizes the same goal."""
from .models import Route

W_DIST = 10.0        # cost per km driven
W_LATE = 6.0         # cost per minute late (before priority multiplier)
W_BAL = 4.0          # penalty on sum of (stops per agent)^2 -> workload balance
W_DROP = 5000.0      # cost of leaving an order unassigned (last resort)
PRIORITY_MULT = {1: 1.0, 2: 2.5, 3: 5.0}


def late_cost(late_min: float, priority: int) -> float:
    return W_LATE * late_min * PRIORITY_MULT.get(priority, 1.0)


def route_cost(route: Route, orders) -> float:
    c = W_DIST * route.distance_km
    for s in route.stops:
        c += late_cost(s.late, orders[s.order_id].priority)
    return c
