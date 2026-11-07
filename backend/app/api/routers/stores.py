from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Store, User
from app.schemas.common import StoreOut
from app.services.geo import haversine_km

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("", response_model=list[StoreOut])
def list_stores(radius_km: float = 20.0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stores = db.scalars(select(Store)).all()
    result = []
    for s in stores:
        d = None
        if current_user.latitude and current_user.longitude:
            d = haversine_km(current_user.latitude, current_user.longitude, s.latitude, s.longitude)
            if d > radius_km:
                continue
            d = round(d, 2)
        result.append(StoreOut(**{c: getattr(s, c) for c in ["id", "name", "chain", "address", "area_label", "latitude", "longitude"]}, distance_km=d))
    result.sort(key=lambda x: (x.distance_km is None, x.distance_km or 9999))
    return result
