from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Recipe, RecipeIngredient
from app.schemas.common import RecipeIngredientOut, RecipeOut

router = APIRouter(prefix="/recipes", tags=["recipes"])


def _recipe_out(r: Recipe) -> RecipeOut:
    return RecipeOut(
        id=r.id,
        name=r.name,
        description=r.description,
        cuisine=r.cuisine,
        prep_minutes=r.prep_minutes,
        cook_minutes=r.cook_minutes,
        servings=r.servings,
        dietary_tags=r.dietary_tags,
        instructions=r.instructions,
        image_url=r.image_url,
        ingredients=[
            RecipeIngredientOut(
                ingredient_id=ri.ingredient_id,
                ingredient_name=ri.ingredient.name,
                category=ri.ingredient.category,
                quantity=ri.quantity,
                unit=ri.unit,
                notes=ri.notes,
            )
            for ri in r.ingredients
        ],
    )


@router.get("", response_model=list[RecipeOut])
def list_recipes(
    q: str | None = None,
    cuisine: str | None = None,
    ingredient: str | None = None,
    dietary: str | None = None,
    max_minutes: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    stmt = select(Recipe)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Recipe.name).like(like),
                func.lower(Recipe.description).like(like),
                func.lower(Recipe.cuisine).like(like),
            )
        )
    if cuisine:
        stmt = stmt.where(func.lower(Recipe.cuisine).like(f"%{cuisine.lower()}%"))
    if dietary:
        stmt = stmt.where(func.lower(Recipe.dietary_tags).like(f"%{dietary.lower()}%"))

    if max_minutes is not None:
        stmt = stmt.where((Recipe.prep_minutes + Recipe.cook_minutes) <= max_minutes)
    recipes = db.scalars(stmt.order_by(Recipe.name.asc())).all()
    if ingredient:
        needle = ingredient.lower()
        recipes = [r for r in recipes if any(needle in ri.ingredient.name.lower() for ri in r.ingredients)]
    return [_recipe_out(r) for r in recipes]


@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    r = db.get(Recipe, recipe_id)
    if not r:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Recipe not found")
    return _recipe_out(r)
