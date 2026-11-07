from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    profile_picture: str | None = None
    location_label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    share_exact_location: bool | None = None
    shopping_radius_km: float | None = Field(default=None, ge=0.5, le=100)
    dietary_preferences: str | None = None
    allergies: str | None = None
    weekly_budget: float | None = Field(default=None, ge=0)
    meal_prep_preferences: str | None = None


class UserOut(ORMModel):
    id: int
    email: EmailStr
    name: str
    profile_picture: str | None
    location_label: str | None
    latitude: float | None = None
    longitude: float | None = None
    share_exact_location: bool
    shopping_radius_km: float
    dietary_preferences: str
    allergies: str
    weekly_budget: float | None
    meal_prep_preferences: str


class PublicUserOut(ORMModel):
    id: int
    name: str
    profile_picture: str | None
    location_label: str | None
    distance_km: float | None = None
    dietary_preferences: str
    allergies: str
    meal_prep_preferences: str
    weekly_budget: float | None


class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str = ""
    area_label: str = ""
    latitude: float | None = None
    longitude: float | None = None
    join_mode: str = Field(default="request", pattern="^(request|invite)$")


class GroupOut(ORMModel):
    id: int
    name: str
    description: str
    area_label: str
    latitude: float | None
    longitude: float | None
    join_mode: str
    created_by: int
    member_count: int = 0
    distance_km: float | None = None


class GroupDetailOut(GroupOut):
    is_member: bool = False
    my_role: str | None = None
    join_request_status: str | None = None


class MemberOut(ORMModel):
    id: int
    user_id: int
    name: str
    profile_picture: str | None
    role: str
    joined_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageOut(ORMModel):
    id: int
    group_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime


class RecipeIngredientOut(ORMModel):
    ingredient_id: int
    ingredient_name: str
    category: str
    quantity: float
    unit: str
    notes: str


class RecipeOut(ORMModel):
    id: int
    name: str
    description: str
    cuisine: str
    prep_minutes: int
    cook_minutes: int
    servings: int
    dietary_tags: str
    instructions: str
    image_url: str | None
    ingredients: list[RecipeIngredientOut] = []


class MealPlanCreate(BaseModel):
    week_start: date
    portions_per_member: int = Field(default=1, ge=1, le=10)


class MealPlanRecipeCreate(BaseModel):
    recipe_id: int


class VoteCreate(BaseModel):
    value: int



class MealPlanRecipeOut(ORMModel):
    id: int
    recipe_id: int
    recipe_name: str
    proposed_by: int
    approved: bool
    votes: int = 0


class MealPlanOut(ORMModel):
    id: int
    group_id: int
    week_start: date
    status: str
    portions_per_member: int
    recipes: list[MealPlanRecipeOut] = []


class ConsolidatedIngredientOut(BaseModel):
    ingredient_id: int
    ingredient_name: str
    category: str
    total_quantity: float
    unit: str
    source_recipes: list[str]


class StoreOut(ORMModel):
    id: int
    name: str
    chain: str
    address: str
    area_label: str
    latitude: float
    longitude: float
    distance_km: float | None = None


class PriceOptionOut(BaseModel):
    store: StoreOut
    brand: str
    package_size: float
    unit: str
    price: float
    available: bool
    is_simulated: bool
    price_per_unit: float
    packages_needed: int
    total_cost: float
    score: float


class IngredientComparisonOut(BaseModel):
    ingredient_id: int
    ingredient_name: str
    required_quantity: float
    unit: str
    options: list[PriceOptionOut]
    best_option: PriceOptionOut | None
    prices_are_simulated: bool = True


class ShoppingItemOut(ORMModel):
    id: int
    ingredient_id: int
    store_product_id: int | None
    description: str
    quantity: float
    unit: str
    estimated_price: float
    purchased: bool


class ShoppingAssignmentOut(ORMModel):
    id: int
    meal_plan_id: int
    user_id: int
    user_name: str
    store_id: int | None
    store_name: str | None
    estimated_total: float
    status: str
    items: list[ShoppingItemOut] = []


class CookingSessionCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    meal_plan_id: int | None = None
    scheduled_at: datetime | None = None
    notes: str = ""


class CookingSessionOut(ORMModel):
    id: int
    group_id: int
    meal_plan_id: int | None
    title: str
    scheduled_at: datetime | None
    status: str
    notes: str
