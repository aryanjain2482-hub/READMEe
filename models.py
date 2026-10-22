"""Data models for RouteWise."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Depot(BaseModel):
    lat: float
    lng: float
    name: str = "Central Depot"


class Agent(BaseModel):
    id: str
    name: str
    capacity: int = 10         # max packages the vehicle can carry
    available: bool = True


class Order(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    demand: int = 1            # packages in this order
    priority: int = 1          # 1 = normal, 2 = high, 3 = urgent
    tw_start: int = 0          # time window start, minutes from shift start
    tw_end: int = 480          # time window end, minutes from shift start
    service_time: int = 5      # minutes spent at the customer
    status: str = "pending"    # pending | cancelled | delayed
    delay: int = 0             # extra minutes added to tw_start when delayed
    locked_agent: Optional[str] = None  # set when manually reassigned


class Stop(BaseModel):
    order_id: str
    arrival: float             # minutes from shift start
    wait: float = 0.0
    late: float = 0.0          # minutes past tw_end (0 if on time)


class Route(BaseModel):
    agent_id: str
    stops: List[Stop] = Field(default_factory=list)
    distance_km: float = 0.0
    duration_min: float = 0.0
    load: int = 0


class Metrics(BaseModel):
    total_distance_km: float
    total_duration_min: float
    late_deliveries: int
    total_late_minutes: float
    unassigned: int
    balance_gap: int           # max stops - min stops across active agents
    priority_late: int         # late deliveries among high/urgent orders


class Solution(BaseModel):
    method: str
    routes: List[Route]
    unassigned: List[str]
    metrics: Metrics
    solve_ms: float = 0.0


class Scenario(BaseModel):
    depot: Depot
    agents: List[Agent]
    orders: List[Order]
