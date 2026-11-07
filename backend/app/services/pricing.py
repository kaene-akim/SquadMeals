import math

from sqlalchemy.orm import Session

from app.models import Store, StoreProduct
from app.services.geo import haversine_km


def compare_prices(
    db: Session,
    ingredient_id: int,
    required_quantity: float,
    unit: str,
    user_lat: float | None = None,
    user_lng: float | None = None,
    max_distance_km: float = 25.0,
) -> list[dict]:
    """Compare simulated/real store prices. Interface can later delegate to retailer APIs."""
    rows = (
        db.query(StoreProduct, Store)
        .join(Store, Store.id == StoreProduct.store_id)
        .filter(StoreProduct.ingredient_id == ingredient_id, StoreProduct.available.is_(True))
        .all()
    )
    options = []
    for sp, store in rows:
        # simple unit compatibility: treat same unit family as compatible for MVP
        if sp.unit != unit and not _compatible(unit, sp.unit):
            continue
        req = _convert(required_quantity, unit, sp.unit)
        pkg = max(sp.package_size, 0.001)
        packages_needed = max(1, math.ceil(req / pkg))
        total_cost = round(packages_needed * sp.price, 2)
        ppu = sp.price / pkg
        distance = None
        if user_lat is not None and user_lng is not None:
            distance = haversine_km(user_lat, user_lng, store.latitude, store.longitude)
            if distance > max_distance_km:
                continue
        travel_penalty = (distance or 0) * 0.08
        score = total_cost + travel_penalty
        options.append(
            {
                "store": {
                    "id": store.id,
                    "name": store.name,
                    "chain": store.chain,
                    "address": store.address,
                    "area_label": store.area_label,
                    "latitude": store.latitude,
                    "longitude": store.longitude,
                    "distance_km": round(distance, 2) if distance is not None else None,
                },
                "brand": sp.brand,
                "package_size": sp.package_size,
                "unit": sp.unit,
                "price": sp.price,
                "available": sp.available,
                "is_simulated": sp.is_simulated,
                "price_per_unit": round(ppu, 4),
                "packages_needed": packages_needed,
                "total_cost": total_cost,
                "score": round(score, 4),
                "store_product_id": sp.id,
            }
        )
    options.sort(key=lambda o: (o["score"], o["total_cost"]))
    return options


def _compatible(a: str, b: str) -> bool:
    weights = {"g", "kg"}
    vols = {"ml", "l"}
    return (a in weights and b in weights) or (a in vols and b in vols) or a == b


def _convert(qty: float, from_unit: str, to_unit: str) -> float:
    if from_unit == to_unit:
        return qty
    factors = {"g": 1, "kg": 1000, "ml": 1, "l": 1000}
    if from_unit in factors and to_unit in factors:
        return qty * factors[from_unit] / factors[to_unit]
    return qty
