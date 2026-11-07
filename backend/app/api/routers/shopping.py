from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Group, GroupMember, MealPlan, ShoppingAssignment, ShoppingItem, Store, User
from app.schemas.common import ShoppingAssignmentOut, ShoppingItemOut

router = APIRouter(prefix="/shopping", tags=["shopping"])


@router.get("/my", response_model=list[dict])
def my_assignments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assignments = db.scalars(select(ShoppingAssignment).where(ShoppingAssignment.user_id == current_user.id).order_by(ShoppingAssignment.created_at.desc())).all()
    result = []
    for a in assignments:
        plan = db.get(MealPlan, a.meal_plan_id)
        group = db.get(Group, plan.group_id) if plan else None
        store = db.get(Store, a.store_id) if a.store_id else None
        items = db.scalars(select(ShoppingItem).where(ShoppingItem.assignment_id == a.id)).all()
        result.append(
            {
                "group_id": group.id if group else None,
                "plan_id": a.meal_plan_id,
                "assignment": ShoppingAssignmentOut(
                    id=a.id,
                    meal_plan_id=a.meal_plan_id,
                    user_id=a.user_id,
                    user_name=current_user.name,
                    store_id=a.store_id,
                    store_name=store.name if store else None,
                    estimated_total=a.estimated_total,
                    status=a.status,
                    items=[ShoppingItemOut.model_validate(i) for i in items],
                ),
                "group": {"id": group.id, "name": group.name} if group else None,
                "week_start": plan.week_start.isoformat() if plan else None,
            }
        )
    return result


@router.patch("/assignments/{assignment_id}/items/{item_id}")
def toggle_my_item(assignment_id: int, item_id: int, purchased: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(ShoppingItem, item_id)
    a = db.get(ShoppingAssignment, assignment_id)
    if not item or not a or item.assignment_id != assignment_id:
        raise HTTPException(status_code=404, detail="Item not found")
    plan = db.get(MealPlan, a.meal_plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    # allow any group member to update progress
    member = db.scalar(select(GroupMember).where(GroupMember.group_id == plan.group_id, GroupMember.user_id == current_user.id))
    if not member:
        raise HTTPException(status_code=403, detail="Group membership required")
    item.purchased = purchased
    items = db.scalars(select(ShoppingItem).where(ShoppingItem.assignment_id == assignment_id)).all()
    if all(i.purchased for i in items):
        a.status = "done"
    elif any(i.purchased for i in items):
        a.status = "in_progress"
    else:
        a.status = "assigned"
    db.commit()
    return {"purchased": item.purchased, "assignment_status": a.status}

