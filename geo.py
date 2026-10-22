"""Distance / travel-time matrix.

Tries the public OSRM demo server for real road distances. If it is
unreachable (no internet, rate limit, timeout) it silently falls back to
haversine distance * a road-winding factor, so the demo never breaks.
"""
import json
import math
import os
import urllib.request
from typing import List, Tuple

AVG_SPEED_KMPH = 25.0     # city delivery speed
ROAD_FACTOR = 1.3         # straight line -> approx road distance
USE_OSRM = os.environ.get("USE_OSRM", "1") == "1"
OSRM_URL = os.environ.get("OSRM_URL", "https://router.project-osrm.org")

Point = Tuple[float, float]  # (lat, lng)


def haversine_km(a: Point, b: Point) -> float:
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(d))


def _haversine_matrix(points: List[Point]) -> List[List[float]]:
    n = len(points)
    return [[0.0 if i == j else haversine_km(points[i], points[j]) * ROAD_FACTOR
             for j in range(n)] for i in range(n)]


def _osrm_matrix(points: List[Point]):
    coords = ";".join(f"{lng},{lat}" for lat, lng in points)
    url = f"{OSRM_URL}/table/v1/driving/{coords}?annotations=distance"
    with urllib.request.urlopen(url, timeout=4) as resp:
        data = json.loads(resp.read().decode())
    if data.get("code") != "Ok":
        raise RuntimeError("OSRM error")
    return [[(v or 0) / 1000.0 for v in row] for row in data["distances"]]


def distance_matrix_km(points: List[Point]) -> Tuple[List[List[float]], str]:
    """Returns (matrix_in_km, source) where source is 'osrm' or 'haversine'."""
    if USE_OSRM and 1 < len(points) <= 80:
        try:
            return _osrm_matrix(points), "osrm"
        except Exception:
            pass
    return _haversine_matrix(points), "haversine"


def km_to_min(km: float) -> float:
    return km / AVG_SPEED_KMPH * 60.0
