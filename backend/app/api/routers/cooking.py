from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_group_member
from app.core.database import get_db
from app.models import CookingSession, MealPlan, User
from app.schemas.common import CookingSessionCreate, CookingSessionOut

router = APIRouter(prefix="/groups/{group_id}/cooking", tags=["cooking"])


@router.get("", response_model=list[CookingSessionOut])
def list_sessions(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    return db.scalars(select(CookingSession).where(CookingSession.group_id == group_id).order_by(CookingSession.created_at.desc())).all()


@router.post("", response_model=CookingSessionOut)
def create_session(group_id: int, payload: CookingSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    if payload.meal_plan_id:
        mp = db.get(MealPlan, payload.meal_plan_id)
        if not mp or mp.group_id != group_id:
            raise HTTPException(status_code=400, detail="Invalid meal plan")
    s = CookingSession(group_id=group_id, **payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.patch("/{session_id}", response_model=CookingSessionOut)
def update_session(group_id: int, session_id: int, status: str | None = None, notes: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    s = db.get(CookingSession, session_id)
    if not s or s.group_id != group_id:
        raise HTTPException(status_code=404, detail="Session not found")
    if status:
        if status not in {"planned", "in_progress", "done"}:
            raise HTTPException(status_code=400, detail="Invalid status")
        s.status = status
    if notes is not None:
        s.notes = notes
    db.commit()
    db.refresh(s)
    return s
