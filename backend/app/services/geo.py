import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two coordinates in km. PostGIS can replace this later."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def within_radius(lat1: float | None, lon1: float | None, lat2: float | None, lon2: float | None, radius_km: float) -> tuple[bool, float | None]:
    if None in (lat1, lon1, lat2, lon2):
        return True, None
    d = haversine_km(lat1, lon1, lat2, lon2)  # type: ignore[arg-type]
    return d <= radius_km, round(d, 2)
