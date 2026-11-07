from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import GroupMember, ShoppingAssignment, ShoppingItem, Store, StoreProduct, User
from app.services.geo import haversine_km
from app.services.pricing import compare_prices


def generate_allocation(db: Session, meal_plan_id: int, consolidated: list[dict]) -> list[ShoppingAssignment]:
    """Heuristic allocator behind a stable interface; OR-Tools can replace internals later.

    Goals: minimize combined estimated grocery + travel cost, and spread item burden fairly.
    Prices/items may be simulated in MVP.
    """
    meal_plan_group_id = db.execute(
        __import__("sqlalchemy").select(__import__("app.models", fromlist=["MealPlan"]).MealPlan.group_id).where(
            __import__("app.models", fromlist=["MealPlan"]).MealPlan.id == meal_plan_id
        )
    ).scalar_one()

    members = db.query(GroupMember, User).join(User, User.id == GroupMember.user_id).filter(GroupMember.group_id == meal_plan_group_id).all()
    if not members:
        return []

    # clear previous assignments for this plan
    old = db.query(ShoppingAssignment).filter(ShoppingAssignment.meal_plan_id == meal_plan_id).all()
    for a in old:
        db.delete(a)
    db.flush()

    assignments: dict[int, ShoppingAssignment] = {}
    burden: dict[int, float] = defaultdict(float)
    for _, user in members:
        a = ShoppingAssignment(meal_plan_id=meal_plan_id, user_id=user.id, estimated_total=0.0, status="assigned")
        db.add(a)
        db.flush()
        assignments[user.id] = a
        burden[user.id] = 0.0

    for ing in consolidated:
        # pick member+option that balances cost and fairness
        best = None
        for _, user in members:
            opts = compare_prices(
                db,
                ing["ingredient_id"],
                ing["total_quantity"],
                ing["unit"],
                user.latitude,
                user.longitude,
            )
            if not opts:
                opts = compare_prices(db, ing["ingredient_id"], ing["total_quantity"], ing["unit"])
            if not opts:
                continue
            opt = opts[0]
            fairness_penalty = burden[user.id] * 0.35
            dist = opt["store"].get("distance_km") or 0
            candidate = (opt["total_cost"] + dist * 0.1 + fairness_penalty, opt["total_cost"], user.id, opt)
            if best is None or candidate < best:
                best = candidate
        if best is None:
            # unassigned fallback to first member
            uid = members[0][1].id
            item = ShoppingItem(
                assignment_id=assignments[uid].id,
                ingredient_id=ing["ingredient_id"],
                description=f'{ing["ingredient_name"]} (no price data found)',
                quantity=ing["total_quantity"],
                unit=ing["unit"],
                estimated_price=0.0,
            )
            db.add(item)
            burden[uid] += 1
            continue
        _, cost, uid, opt = best
        a = assignments[uid]
        if not a.store_id:
            a.store_id = opt["store"]["id"]
        item = ShoppingItem(
            assignment_id=a.id,
            ingredient_id=ing["ingredient_id"],
            store_product_id=opt.get("store_product_id"),
            description=f'{ing["ingredient_name"]} - {opt["brand"]} @ {opt["store"]["name"]}',
            quantity=ing["total_quantity"],
            unit=ing["unit"],
            estimated_price=cost,
        )
        db.add(item)
        a.estimated_total = round(a.estimated_total + cost, 2)
        burden[uid] += cost

    db.commit()
    for a in assignments.values():
        db.refresh(a)
    return list(assignments.values())
