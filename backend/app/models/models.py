from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    hashed_password: Mapped[str] = mapped_column(String(255))
    profile_picture: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    share_exact_location: Mapped[bool] = mapped_column(Boolean, default=False)
    shopping_radius_km: Mapped[float] = mapped_column(Float, default=5.0)
    dietary_preferences: Mapped[str] = mapped_column(String(500), default="")
    allergies: Mapped[str] = mapped_column(String(500), default="")
    weekly_budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    meal_prep_preferences: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    memberships: Mapped[list[GroupMember]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    area_label: Mapped[str] = mapped_column(String(200), default="")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    join_mode: Mapped[str] = mapped_column(String(20), default="request")  # request|invite
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    members: Mapped[list[GroupMember]] = relationship(back_populates="group", cascade="all, delete-orphan")
    messages: Mapped[list[GroupMessage]] = relationship(back_populates="group", cascade="all, delete-orphan")
    meal_plans: Mapped[list[MealPlan]] = relationship(back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_member"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), default="member")  # admin|member
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    group: Mapped[Group] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="memberships")


class GroupJoinRequest(Base):
    __tablename__ = "group_join_requests"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_join_request"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|approved|rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class GroupMessage(Base):
    __tablename__ = "group_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    group: Mapped[Group] = relationship(back_populates="messages")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    cuisine: Mapped[str] = mapped_column(String(80), default="")
    prep_minutes: Mapped[int] = mapped_column(Integer, default=20)
    cook_minutes: Mapped[int] = mapped_column(Integer, default=20)
    servings: Mapped[int] = mapped_column(Integer, default=4)
    dietary_tags: Mapped[str] = mapped_column(String(300), default="")  # comma-separated
    instructions: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    ingredients: Mapped[list[RecipeIngredient]] = relationship(back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80), default="general")
    default_unit: Mapped[str] = mapped_column(String(30), default="unit")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), index=True)
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str] = mapped_column(String(200), default="")

    recipe: Mapped[Recipe] = relationship(back_populates="ingredients")
    ingredient: Mapped[Ingredient] = relationship()


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    week_start: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft|finalized
    portions_per_member: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    group: Mapped[Group] = relationship(back_populates="meal_plans")
    recipes: Mapped[list[MealPlanRecipe]] = relationship(back_populates="meal_plan", cascade="all, delete-orphan")


class MealPlanRecipe(Base):
    __tablename__ = "meal_plan_recipes"
    __table_args__ = (UniqueConstraint("meal_plan_id", "recipe_id", name="uq_meal_plan_recipe"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_plan_id: Mapped[int] = mapped_column(ForeignKey("meal_plans.id", ondelete="CASCADE"), index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), index=True)
    proposed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)

    meal_plan: Mapped[MealPlan] = relationship(back_populates="recipes")
    recipe: Mapped[Recipe] = relationship()
    votes: Mapped[list[MealPlanVote]] = relationship(back_populates="meal_plan_recipe", cascade="all, delete-orphan")


class MealPlanVote(Base):
    __tablename__ = "meal_plan_votes"
    __table_args__ = (UniqueConstraint("meal_plan_recipe_id", "user_id", name="uq_meal_plan_vote"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_plan_recipe_id: Mapped[int] = mapped_column(ForeignKey("meal_plan_recipes.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    value: Mapped[int] = mapped_column(Integer, default=1)  # 1 up, -1 down

    meal_plan_recipe: Mapped[MealPlanRecipe] = relationship(back_populates="votes")


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    chain: Mapped[str] = mapped_column(String(120), default="")
    address: Mapped[str] = mapped_column(String(300), default="")
    area_label: Mapped[str] = mapped_column(String(200), default="")
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)


class StoreProduct(Base):
    __tablename__ = "store_products"
    __table_args__ = (UniqueConstraint("store_id", "ingredient_id", "brand", "package_size", name="uq_store_product"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), index=True)
    brand: Mapped[str] = mapped_column(String(120), default="Generic")
    package_size: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Float)
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True)

    store: Mapped[Store] = relationship()
    ingredient: Mapped[Ingredient] = relationship()


class ShoppingAssignment(Base):
    __tablename__ = "shopping_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meal_plan_id: Mapped[int] = mapped_column(ForeignKey("meal_plans.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    estimated_total: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="assigned")  # assigned|in_progress|done
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items: Mapped[list[ShoppingItem]] = relationship(back_populates="assignment", cascade="all, delete-orphan")


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("shopping_assignments.id", ondelete="CASCADE"), index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    store_product_id: Mapped[int | None] = mapped_column(ForeignKey("store_products.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(250))
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30))
    estimated_price: Mapped[float] = mapped_column(Float, default=0.0)
    purchased: Mapped[bool] = mapped_column(Boolean, default=False)

    assignment: Mapped[ShoppingAssignment] = relationship(back_populates="items")


class CookingSession(Base):
    __tablename__ = "cooking_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    meal_plan_id: Mapped[int | None] = mapped_column(ForeignKey("meal_plans.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(200))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="planned")  # planned|in_progress|done
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
