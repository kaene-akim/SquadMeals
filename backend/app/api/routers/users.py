from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.common import PublicUserOut, UserOut, UserUpdate
from app.services.geo import haversine_km

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(current_user, k, v)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/nearby", response_model=list[PublicUserOut])
def nearby_users(
    radius_km: float = 10.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = db.scalars(select(User).where(User.id != current_user.id)).all()
    result = []
    for u in users:
        if not (current_user.latitude and current_user.longitude and u.latitude and u.longitude):
            continue
        d = haversine_km(current_user.latitude, current_user.longitude, u.latitude, u.longitude)
        search_radius = min(radius_km, current_user.shopping_radius_km or radius_km)
        if d <= search_radius:
            result.append(
                PublicUserOut(
                    id=u.id,
                    name=u.name,
                    profile_picture=u.profile_picture,
                    location_label=u.location_label or "Nearby area",
                    distance_km=round(d, 2),
                    dietary_preferences=u.dietary_preferences,
                    allergies=u.allergies,
                    meal_prep_preferences=u.meal_prep_preferences,
                    weekly_budget=u.weekly_budget,
                )
            )
    result.sort(key=lambda x: x.distance_km or 9999)
    return result
