from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_group_member
from app.core.database import get_db
from app.models import (
    GroupMember,
    Ingredient,
    MealPlan,
    MealPlanRecipe,
    MealPlanVote,
    Recipe,
    ShoppingAssignment,
    ShoppingItem,
    Store,
    User,
)
from app.schemas.common import (
    ConsolidatedIngredientOut,
    IngredientComparisonOut,
    MealPlanCreate,
    MealPlanOut,
    MealPlanRecipeCreate,
    MealPlanRecipeOut,
    PriceOptionOut,
    ShoppingAssignmentOut,
    ShoppingItemOut,
    StoreOut,
    VoteCreate,
)
from app.services.allocation import generate_allocation
from app.services.planning import consolidate_ingredients
from app.services.pricing import compare_prices

router = APIRouter(prefix="/groups/{group_id}/plans", tags=["meal-plans"])


def _plan_out(db: Session, plan: MealPlan) -> MealPlanOut:
    recipes = []
    for mpr in plan.recipes:
        recipe = db.get(Recipe, mpr.recipe_id)
        votes = db.scalar(select(func.coalesce(func.sum(MealPlanVote.value), 0)).where(MealPlanVote.meal_plan_recipe_id == mpr.id)) or 0
        recipes.append(
            MealPlanRecipeOut(
                id=mpr.id,
                recipe_id=mpr.recipe_id,
                recipe_name=recipe.name if recipe else "Unknown",
                proposed_by=mpr.proposed_by,
                approved=mpr.approved,
                votes=int(votes),
            )
        )
    return MealPlanOut(id=plan.id, group_id=plan.group_id, week_start=plan.week_start, status=plan.status, portions_per_member=plan.portions_per_member, recipes=recipes)


@router.get("", response_model=list[MealPlanOut])
def list_plans(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plans = db.scalars(select(MealPlan).where(MealPlan.group_id == group_id).order_by(MealPlan.week_start.desc())).all()
    return [_plan_out(db, p) for p in plans]


@router.post("", response_model=MealPlanOut)
def create_plan(group_id: int, payload: MealPlanCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = MealPlan(group_id=group_id, week_start=payload.week_start, portions_per_member=payload.portions_per_member)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return _plan_out(db, plan)


@router.post("/{plan_id}/recipes", response_model=MealPlanOut)
def propose_recipe(group_id: int, plan_id: int, payload: MealPlanRecipeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = db.get(MealPlan, plan_id)
    if not plan or plan.group_id != group_id:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    if not db.get(Recipe, payload.recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")
    existing = db.scalar(select(MealPlanRecipe).where(MealPlanRecipe.meal_plan_id == plan_id, MealPlanRecipe.recipe_id == payload.recipe_id))
    if not existing:
        db.add(MealPlanRecipe(meal_plan_id=plan_id, recipe_id=payload.recipe_id, proposed_by=current_user.id))
        db.commit()
        db.refresh(plan)
    return _plan_out(db, plan)


@router.post("/{plan_id}/recipes/{recipe_row_id}/vote", response_model=MealPlanOut)
def vote_recipe(group_id: int, plan_id: int, recipe_row_id: int, payload: VoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    if payload.value not in (1, -1):
        raise HTTPException(status_code=400, detail="Vote must be 1 or -1")
    plan = db.get(MealPlan, plan_id)
    mpr = db.get(MealPlanRecipe, recipe_row_id)
    if not plan or plan.group_id != group_id or not mpr or mpr.meal_plan_id != plan_id:
        raise HTTPException(status_code=404, detail="Not found")
    vote = db.scalar(select(MealPlanVote).where(MealPlanVote.meal_plan_recipe_id == recipe_row_id, MealPlanVote.user_id == current_user.id))
    if vote:
        vote.value = payload.value
    else:
        db.add(MealPlanVote(meal_plan_recipe_id=recipe_row_id, user_id=current_user.id, value=payload.value))
    db.commit()
    db.refresh(plan)
    return _plan_out(db, plan)


@router.post("/{plan_id}/recipes/{recipe_row_id}/approve", response_model=MealPlanOut)
def approve_recipe(group_id: int, plan_id: int, recipe_row_id: int, approved: bool = True, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = db.get(MealPlan, plan_id)
    mpr = db.get(MealPlanRecipe, recipe_row_id)
    if not plan or plan.group_id != group_id or not mpr or mpr.meal_plan_id != plan_id:
        raise HTTPException(status_code=404, detail="Not found")
    mpr.approved = approved
    db.commit()
    db.refresh(plan)
    return _plan_out(db, plan)


@router.post("/{plan_id}/finalize", response_model=MealPlanOut)
def finalize_plan(group_id: int, plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = db.get(MealPlan, plan_id)
    if not plan or plan.group_id != group_id:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    if not any(r.approved for r in plan.recipes):
        raise HTTPException(status_code=400, detail="Approve at least one recipe before finalizing")
    plan.status = "finalized"
    db.commit()
    db.refresh(plan)
    return _plan_out(db, plan)


@router.get("/{plan_id}/ingredients", response_model=list[ConsolidatedIngredientOut])
def ingredients(group_id: int, plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = db.get(MealPlan, plan_id)
    if not plan or plan.group_id != group_id:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return consolidate_ingredients(db, plan)


@router.get("/{plan_id}/price-comparison", response_model=list[IngredientComparisonOut])
def price_comparison(group_id: int, plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = db.get(MealPlan, plan_id)
    if not plan or plan.group_id != group_id:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    consolidated = consolidate_ingredients(db, plan)
    result = []
    for row in consolidated:
        opts = compare_prices(db, row["ingredient_id"], row["total_quantity"], row["unit"], current_user.latitude, current_user.longitude)
        parsed = [PriceOptionOut(**o) for o in opts]
        result.append(
            IngredientComparisonOut(
                ingredient_id=row["ingredient_id"],
                ingredient_name=row["ingredient_name"],
                required_quantity=row["total_quantity"],
                unit=row["unit"],
                options=parsed,
                best_option=parsed[0] if parsed else None,
                prices_are_simulated=any(o.is_simulated for o in parsed) if parsed else True,
            )
        )
    return result


@router.post("/{plan_id}/allocate", response_model=list[ShoppingAssignmentOut])
def allocate(group_id: int, plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = db.get(MealPlan, plan_id)
    if not plan or plan.group_id != group_id:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    consolidated = consolidate_ingredients(db, plan)
    if not consolidated:
        raise HTTPException(status_code=400, detail="No approved recipes/ingredients to allocate")
    generate_allocation(db, plan_id, consolidated)
    return get_assignments(group_id, plan_id, db, current_user)


@router.get("/{plan_id}/assignments", response_model=list[ShoppingAssignmentOut])
def get_assignments(group_id: int, plan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    plan = db.get(MealPlan, plan_id)
    if not plan or plan.group_id != group_id:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    assignments = db.scalars(select(ShoppingAssignment).where(ShoppingAssignment.meal_plan_id == plan_id)).all()
    result = []
    for a in assignments:
        u = db.get(User, a.user_id)
        s = db.get(Store, a.store_id) if a.store_id else None
        items = db.scalars(select(ShoppingItem).where(ShoppingItem.assignment_id == a.id)).all()
        result.append(
            ShoppingAssignmentOut(
                id=a.id,
                meal_plan_id=a.meal_plan_id,
                user_id=a.user_id,
                user_name=u.name if u else "Member",
                store_id=a.store_id,
                store_name=s.name if s else None,
                estimated_total=a.estimated_total,
                status=a.status,
                items=[ShoppingItemOut.model_validate(i) for i in items],
            )
        )
    return result


@router.patch("/{plan_id}/assignments/{assignment_id}/items/{item_id}")
def toggle_item(group_id: int, plan_id: int, assignment_id: int, item_id: int, purchased: bool, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    item = db.get(ShoppingItem, item_id)
    if not item or item.assignment_id != assignment_id:
        raise HTTPException(status_code=404, detail="Item not found")
    a = db.get(ShoppingAssignment, assignment_id)
    if not a or a.meal_plan_id != plan_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if a.user_id != current_user.id:
        # allow group progress visibility but restrict edits? MVP: allow group members to help update
        pass
    item.purchased = purchased
    # auto status
    items = db.scalars(select(ShoppingItem).where(ShoppingItem.assignment_id == assignment_id)).all()
    if all(i.purchased for i in items):
        a.status = "done"
    elif any(i.purchased for i in items):
        a.status = "in_progress"
    db.commit()
    return {"purchased": item.purchased, "assignment_status": a.status}
