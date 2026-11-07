from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import (
    CookingSession,
    Group,
    GroupMember,
    Ingredient,
    MealPlan,
    MealPlanRecipe,
    Recipe,
    RecipeIngredient,
    Store,
    StoreProduct,
    User,
)


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(User.id)):
        return

    # Sample area: Maplewood / central Portland-like coordinates for realistic discovery.
    # Grocery prices below are SIMULATED sample data for the MVP demo.
    users = [
        User(email="demo@squadmeals.app", name="Alex Demo", hashed_password=get_password_hash("password123"), location_label="Maplewood, North Block", latitude=45.5231, longitude=-122.6765, shopping_radius_km=8, dietary_preferences="balanced", allergies="", weekly_budget=60, meal_prep_preferences="batch cooking, vegetarian-friendly options"),
        User(email="sam@example.com", name="Sam Rivera", hashed_password=get_password_hash("password123"), location_label="Maplewood, East Side", latitude=45.5218, longitude=-122.6689, shopping_radius_km=6, dietary_preferences="high-protein", allergies="peanuts", weekly_budget=75, meal_prep_preferences="quick lunches"),
        User(email="maria@example.com", name="Maria Chen", hashed_password=get_password_hash("password123"), location_label="Maplewood, South Market", latitude=45.5169, longitude=-122.6784, shopping_radius_km=10, dietary_preferences="vegetarian", allergies="", weekly_budget=55, meal_prep_preferences="family-style dinners"),
        User(email="jordan@example.com", name="Jordan Patel", hashed_password=get_password_hash("password123"), location_label="Maplewood, West Park", latitude=45.5254, longitude=-122.6841, shopping_radius_km=7, dietary_preferences="no pork", allergies="shellfish", weekly_budget=65, meal_prep_preferences="meal prep Sundays"),
    ]
    db.add_all(users)
    db.flush()

    group = Group(name="Maplewood Meal Squad", description="Neighbours planning affordable weekly meals together.", area_label="Maplewood", latitude=45.5225, longitude=-122.6760, join_mode="request", created_by=users[0].id)
    db.add(group)
    db.flush()
    db.add_all([
        GroupMember(group_id=group.id, user_id=users[0].id, role="admin"),
        GroupMember(group_id=group.id, user_id=users[1].id, role="member"),
        GroupMember(group_id=group.id, user_id=users[2].id, role="member"),
        GroupMember(group_id=group.id, user_id=users[3].id, role="member"),
    ])

    ing_data = [
        ("chicken breast", "protein", "kg"), ("potatoes", "produce", "kg"), ("onions", "produce", "kg"),
        ("frozen mixed vegetables", "frozen", "bag"), ("olive oil", "pantry", "l"), ("rice", "pantry", "kg"),
        ("canned tomatoes", "pantry", "can"), ("garlic", "produce", "kg"), ("carrots", "produce", "kg"),
        ("bell pepper", "produce", "kg"), ("black beans", "pantry", "can"), ("tortillas", "bakery", "pack"),
        ("cheddar cheese", "dairy", "kg"), ("eggs", "dairy", "pack"), ("spinach", "produce", "kg"),
        ("pasta", "pantry", "kg"), ("tomato passata", "pantry", "l"), ("chickpeas", "pantry", "can"),
        ("cucumber", "produce", "kg"), ("greek yogurt", "dairy", "kg"), ("lemon", "produce", "kg"),
        ("oats", "pantry", "kg"), ("milk", "dairy", "l"), ("banana", "produce", "kg"),
    ]
    ingredients = {name: Ingredient(name=name, category=cat, default_unit=unit) for name, cat, unit in ing_data}
    db.add_all(ingredients.values())
    db.flush()

    def add_recipe(name, desc, cuisine, prep, cook, servings, tags, instructions, items, image=None):
        r = Recipe(name=name, description=desc, cuisine=cuisine, prep_minutes=prep, cook_minutes=cook, servings=servings, dietary_tags=tags, instructions=instructions, image_url=image)
        db.add(r)
        db.flush()
        for iname, qty, unit, notes in items:
            db.add(RecipeIngredient(recipe_id=r.id, ingredient_id=ingredients[iname].id, quantity=qty, unit=unit, notes=notes))
        return r

    r1 = add_recipe(
        "One-Pan Lemon Chicken & Potatoes", "A budget-friendly batch meal with roasted vegetables.", "Mediterranean", 15, 35, 4, "high-protein,gluten-free",
        "1. Heat oven to 200°C. 2. Toss chicken, potatoes, onions and carrots with olive oil, lemon and seasoning. 3. Roast 35 minutes until cooked through. 4. Portion for the week.",
        [("chicken breast", 0.8, "kg", ""), ("potatoes", 1.0, "kg", "cubed"), ("onions", 0.3, "kg", ""), ("olive oil", 0.05, "l", ""), ("garlic", 0.02, "kg", ""), ("carrots", 0.4, "kg", ""), ("lemon", 0.15, "kg", "")],
    )
    r2 = add_recipe(
        "Hearty Veggie Rice Bowls", "Colourful meal-prep bowls with beans and frozen vegetables.", "International", 10, 25, 4, "vegetarian,vegan-option,gluten-free",
        "1. Cook rice. 2. Sauté onions, garlic and bell pepper. 3. Add frozen vegetables, tomatoes and black beans. 4. Serve over rice.",
        [("rice", 0.5, "kg", ""), ("frozen mixed vegetables", 1.0, "bag", ""), ("onions", 0.2, "kg", ""), ("canned tomatoes", 1.0, "can", ""), ("garlic", 0.02, "kg", ""), ("bell pepper", 0.3, "kg", ""), ("black beans", 1.0, "can", "drained"), ("olive oil", 0.03, "l", "")],
    )
    r3 = add_recipe(
        "Spinach & Chickpea Pasta", "A fast vegetarian pasta with pantry staples.", "Italian-inspired", 10, 15, 4, "vegetarian",
        "1. Boil pasta. 2. Warm passata with garlic and chickpeas. 3. Fold in spinach. 4. Combine and portion.",
        [("pasta", 0.4, "kg", ""), ("tomato passata", 0.5, "l", ""), ("chickpeas", 1.0, "can", ""), ("spinach", 0.2, "kg", ""), ("garlic", 0.015, "kg", ""), ("olive oil", 0.02, "l", "")],
    )
    add_recipe(
        "Breakfast Oat Jars", "Simple prep-ahead breakfasts.", "Breakfast", 10, 0, 4, "vegetarian",
        "1. Combine oats, milk and yogurt. 2. Add sliced banana. 3. Refrigerate overnight.",
        [("oats", 0.3, "kg", ""), ("milk", 0.8, "l", ""), ("greek yogurt", 0.3, "kg", ""), ("banana", 0.4, "kg", "")],
    )
    add_recipe(
        "Chicken & Bean Wraps", "Easy wraps for lunches.", "Tex-Mex inspired", 15, 15, 4, "high-protein",
        "1. Cook diced chicken with onions and pepper. 2. Add beans. 3. Fill tortillas with chicken mix and cheese.",
        [("chicken breast", 0.5, "kg", ""), ("black beans", 1.0, "can", ""), ("tortillas", 1.0, "pack", "8 wraps"), ("cheddar cheese", 0.2, "kg", ""), ("onions", 0.15, "kg", ""), ("bell pepper", 0.2, "kg", "")],
    )

    stores = [
        Store(name="ValueMart Maplewood", chain="ValueMart", address="12 Cedar Ave", area_label="Maplewood", latitude=45.5205, longitude=-122.6710),
        Store(name="GreenGrocer Local", chain="GreenGrocer", address="88 Market St", area_label="Maplewood", latitude=45.5262, longitude=-122.6815),
        Store(name="Budget Basket", chain="Budget Basket", address="3 Riverside Rd", area_label="Riverside", latitude=45.5150, longitude=-122.6900),
    ]
    db.add_all(stores)
    db.flush()

    # Simulated prices: (store_idx, ingredient, brand, package_size, unit, price)
    # Designed so different stores win on different items.
    prices = [
        (0, "chicken breast", "Farm Select", 1.0, "kg", 8.90), (1, "chicken breast", "Local Farm", 1.0, "kg", 9.80), (2, "chicken breast", "Saver Pack", 1.0, "kg", 8.40),
        (0, "potatoes", "ValueMart", 2.0, "kg", 2.60), (1, "potatoes", "Organic Roots", 1.5, "kg", 3.20), (2, "potatoes", "Budget", 2.5, "kg", 2.90),
        (0, "onions", "ValueMart", 1.0, "kg", 1.40), (1, "onions", "GreenGrocer", 1.0, "kg", 1.55), (2, "onions", "Budget", 1.0, "kg", 1.20),
        (0, "frozen mixed vegetables", "Frosty", 1.0, "bag", 2.10), (1, "frozen mixed vegetables", "Garden Mix", 1.0, "bag", 2.45), (2, "frozen mixed vegetables", "Saver", 1.0, "bag", 1.95),
        (0, "olive oil", "Casa", 1.0, "l", 7.50), (1, "olive oil", "Extra Virgin", 0.75, "l", 6.90), (2, "olive oil", "Everyday", 1.0, "l", 6.80),
        (0, "rice", "Pantry", 1.0, "kg", 2.20), (1, "rice", "Basmati", 1.0, "kg", 2.80), (2, "rice", "Value", 1.0, "kg", 1.95),
        (0, "canned tomatoes", "Pantry", 1.0, "can", 1.10), (1, "canned tomatoes", "Organic", 1.0, "can", 1.45), (2, "canned tomatoes", "Saver", 1.0, "can", 0.95),
        (0, "garlic", "Fresh", 0.1, "kg", 0.90), (1, "garlic", "Local", 0.1, "kg", 0.95), (2, "garlic", "Budget", 0.1, "kg", 0.85),
        (0, "carrots", "Fresh", 1.0, "kg", 1.50), (1, "carrots", "Organic", 1.0, "kg", 1.90), (2, "carrots", "Budget", 1.0, "kg", 1.35),
        (0, "bell pepper", "Fresh", 0.5, "kg", 2.20), (1, "bell pepper", "Local", 0.5, "kg", 2.10), (2, "bell pepper", "Budget", 0.5, "kg", 2.30),
        (0, "black beans", "Pantry", 1.0, "can", 1.00), (1, "black beans", "Organic", 1.0, "can", 1.35), (2, "black beans", "Saver", 1.0, "can", 0.89),
        (0, "tortillas", "Bakery", 1.0, "pack", 2.40), (1, "tortillas", "Whole Wheat", 1.0, "pack", 2.90), (2, "tortillas", "Saver", 1.0, "pack", 2.10),
        (0, "cheddar cheese", "Dairy", 0.4, "kg", 4.80), (1, "cheddar cheese", "Local", 0.4, "kg", 5.20), (2, "cheddar cheese", "Value", 0.5, "kg", 5.40),
        (0, "eggs", "Farm", 1.0, "pack", 3.10), (1, "eggs", "Free Range", 1.0, "pack", 4.20), (2, "eggs", "Saver", 1.0, "pack", 2.85),
        (0, "spinach", "Fresh", 0.2, "kg", 1.80), (1, "spinach", "Local", 0.2, "kg", 1.70), (2, "spinach", "Budget", 0.25, "kg", 2.00),
        (0, "pasta", "Pantry", 0.5, "kg", 1.20), (1, "pasta", "Italian", 0.5, "kg", 1.65), (2, "pasta", "Saver", 0.5, "kg", 0.99),
        (0, "tomato passata", "Pantry", 0.7, "l", 1.90), (1, "tomato passata", "Organic", 0.7, "l", 2.40), (2, "tomato passata", "Saver", 0.7, "l", 1.75),
        (0, "chickpeas", "Pantry", 1.0, "can", 1.05), (1, "chickpeas", "Organic", 1.0, "can", 1.40), (2, "chickpeas", "Saver", 1.0, "can", 0.92),
        (0, "cucumber", "Fresh", 0.5, "kg", 1.30), (1, "cucumber", "Local", 0.5, "kg", 1.25), (2, "cucumber", "Budget", 0.5, "kg", 1.35),
        (0, "greek yogurt", "Dairy", 0.5, "kg", 3.40), (1, "greek yogurt", "Local", 0.5, "kg", 3.60), (2, "greek yogurt", "Value", 0.5, "kg", 3.10),
        (0, "lemon", "Fresh", 0.5, "kg", 2.20), (1, "lemon", "Organic", 0.5, "kg", 2.60), (2, "lemon", "Budget", 0.5, "kg", 2.00),
        (0, "oats", "Pantry", 1.0, "kg", 2.30), (1, "oats", "Wholegrain", 1.0, "kg", 2.70), (2, "oats", "Saver", 1.0, "kg", 2.05),
        (0, "milk", "Dairy", 1.0, "l", 1.25), (1, "milk", "Local", 1.0, "l", 1.45), (2, "milk", "Saver", 1.0, "l", 1.15),
        (0, "banana", "Fresh", 1.0, "kg", 1.60), (1, "banana", "Fairtrade", 1.0, "kg", 1.95), (2, "banana", "Budget", 1.0, "kg", 1.49),
    ]
    for sidx, iname, brand, size, unit, price in prices:
        db.add(StoreProduct(store_id=stores[sidx].id, ingredient_id=ingredients[iname].id, brand=brand, package_size=size, unit=unit, price=price, available=True, is_simulated=True))

    # A sample draft plan so the app is explorable immediately.
    next_monday = date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)
    plan = MealPlan(group_id=group.id, week_start=next_monday, status="draft", portions_per_member=1)
    db.add(plan)
    db.flush()
    db.add_all([
        MealPlanRecipe(meal_plan_id=plan.id, recipe_id=r1.id, proposed_by=users[0].id, approved=True),
        MealPlanRecipe(meal_plan_id=plan.id, recipe_id=r2.id, proposed_by=users[1].id, approved=True),
        MealPlanRecipe(meal_plan_id=plan.id, recipe_id=r3.id, proposed_by=users[2].id, approved=False),
    ])
    db.add(CookingSession(group_id=group.id, meal_plan_id=plan.id, title="Sunday prep session", notes="Bring containers. We’ll batch-cook approved meals."))

    db.commit()
