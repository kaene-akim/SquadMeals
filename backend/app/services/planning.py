from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import GroupMember, Ingredient, MealPlan, MealPlanRecipe, Recipe, RecipeIngredient


def consolidate_ingredients(db: Session, meal_plan: MealPlan) -> list[dict]:
    member_count = db.query(GroupMember).filter(GroupMember.group_id == meal_plan.group_id).count()
    target_portions = max(member_count, 1) * meal_plan.portions_per_member
    approved = [mpr for mpr in meal_plan.recipes if mpr.approved]
    buckets: dict[tuple[int, str], dict] = {}

    for mpr in approved:
        recipe = db.get(Recipe, mpr.recipe_id)
        if not recipe:
            continue
        scale = target_portions / max(recipe.servings, 1)
        for ri in recipe.ingredients:
            ing = ri.ingredient or db.get(Ingredient, ri.ingredient_id)
            if not ing:
                continue
            key = (ing.id, ri.unit)
            if key not in buckets:
                buckets[key] = {
                    "ingredient_id": ing.id,
                    "ingredient_name": ing.name,
                    "category": ing.category,
                    "total_quantity": 0.0,
                    "unit": ri.unit,
                    "source_recipes": [],
                }
            buckets[key]["total_quantity"] += ri.quantity * scale
            if recipe.name not in buckets[key]["source_recipes"]:
                buckets[key]["source_recipes"].append(recipe.name)

    result = list(buckets.values())
    for row in result:
        row["total_quantity"] = round(row["total_quantity"], 2)
    result.sort(key=lambda r: (r["category"], r["ingredient_name"]))
    return result
