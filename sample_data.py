"""Demo scenario: a delivery shift in Indore.

Times are minutes from shift start (shift starts at 09:00).
Coordinates are approximate area centres, good enough for a demo.
"""
from .models import Agent, Depot, Order, Scenario


def sample_scenario() -> Scenario:
    depot = Depot(lat=22.7230, lng=75.8720, name="Central Depot (Geeta Bhawan)")
    agents = [
        Agent(id="A1", name="Ravi", capacity=10),
        Agent(id="A2", name="Priya", capacity=10),
        Agent(id="A3", name="Amit", capacity=10),
    ]
    # (id, name, lat, lng, demand, priority, tw_start, tw_end)
    rows = [
        ("O1",  "Rajwada",        22.7185, 75.8553, 2, 3,   0,  60),
        ("O2",  "Vijay Nagar",    22.7533, 75.8937, 1, 1,  30, 240),
        ("O3",  "Palasia",        22.7244, 75.8839, 1, 2,   0,  90),
        ("O4",  "Bhawarkuan",     22.6987, 75.8680, 3, 1,  60, 300),
        ("O5",  "Annapurna",      22.6925, 75.8317, 1, 1,   0, 360),
        ("O6",  "Rau",            22.6420, 75.8070, 2, 1, 120, 400),
        ("O7",  "Scheme 78",      22.7510, 75.8870, 1, 3,   0,  75),
        ("O8",  "MR-10",          22.7500, 75.9100, 2, 1,  60, 330),
        ("O9",  "Khajrana",       22.7380, 75.9040, 1, 2,  30, 150),
        ("O10", "Airport Road",   22.7217, 75.8011, 2, 1,  90, 420),
        ("O11", "Sudama Nagar",   22.6900, 75.8300, 1, 1,   0, 300),
        ("O12", "Regal Square",   22.7190, 75.8680, 1, 2,  15, 100),
        ("O13", "Bengali Square", 22.7287, 75.9175, 2, 1,  45, 360),
        ("O14", "Mhow Naka",      22.6990, 75.8700, 1, 1,   0, 200),
        ("O15", "LIG Colony",     22.7290, 75.8790, 1, 1,   0, 120),
        ("O16", "Tilak Nagar",    22.7440, 75.8650, 2, 1,  60, 280),
    ]
    orders = [
        Order(id=r[0], name=r[1], lat=r[2], lng=r[3], demand=r[4], priority=r[5],
              tw_start=r[6], tw_end=r[7])
        for r in rows
    ]
    return Scenario(depot=depot, agents=agents, orders=orders)
