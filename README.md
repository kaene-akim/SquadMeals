# SquadMeals

SquadMeals is a social meal-prepping and grocery optimisation MVP. People in the same area can discover each other, form meal-prep groups, plan weekly meals together, consolidate ingredients, compare grocery prices, and split shopping responsibilities fairly.

## What this MVP includes

- **Auth & profiles**: register/login, profile picture URL, location/area, shopping radius, dietary preferences, allergies, weekly budget, meal-prep preferences. Exact coordinates can stay private; discovery uses area labels and distance.
- **Discovery & groups**: find nearby users/groups, create groups, join by request/invitation flow, member list, group discussion.
- **Collaborative meal planning**: browse/search recipes (ingredients, cuisine, time, dietary tags), propose recipes, vote, approve, finalise weekly plans, automatic ingredient consolidation with quantity scaling.
- **Grocery comparison (MVP)**: compares nearby stores/products and finds cheapest suitable options using price per unit, package sizes, required quantities, compatibility, distance and availability.
- **Intelligent shopping allocation**: distributes shopping across members with a cost + distance + fairness heuristic and generates individual shopping lists with progress tracking.
- **Cooking sessions**: schedule and track group cooking/prep sessions.

## Important MVP notes

- **Grocery prices are simulated sample data** in this MVP. The UI/API label them as simulated. The pricing provider and allocation services are separated so real retailer APIs/data feeds can be integrated later.
- **Maps/location**: uses lat/lng + Haversine distance for discovery and store distance. The UI is designed for later Mapbox/Google Maps integration; PostGIS can replace distance logic in production.
- **Auth**: local JWT auth for a zero-setup working MVP. Supabase Auth can replace the auth service behind the same app boundary later.
- **Database**: SQLite for immediate local use; SQLAlchemy models are structured for migration to PostgreSQL/PostGIS.

## Project structure

```text
backend/   FastAPI API, SQLAlchemy models, services, seed data
frontend/  Next.js App Router + Tailwind UI
```

## Run locally

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

On first start, the backend creates `squadmeals.db` and seeds realistic sample users, a group, recipes, stores and **simulated** grocery prices.

### 2. Frontend

```bash
cd frontend
pnpm install
NEXT_PUBLIC_API_BASE=http://localhost:8000/api pnpm dev
```

App: http://localhost:3000

## Demo account

- Email: `demo@squadmeals.app`
- Password: `password123`

The seeded demo user is already in **Maplewood Meal Squad**, which has a draft weekly plan with approved recipes so you can explore consolidation, simulated price comparison and shopping allocation immediately.

## Main user journeys to test

1. Register an account (or sign in as demo).
2. Complete profile location/preferences in **Profile**.
3. Discover and join/request a group in **Discover** / **Groups**.
4. Propose and vote on recipes in a group meal plan.
5. Approve recipes and finalise the weekly meal plan.
6. Generate the consolidated ingredient list.
7. Compare grocery prices (simulated sample data).
8. Generate an individual shopping assignment/allocation.
9. Mark shopping items as complete and see group progress.

## Architecture notes for Stage 2

- Retailer integrations: implement providers behind `backend/app/services/pricing.py`.
- Retailer dashboard: add retailer accounts/catalog/pricing/promotion models and admin UI.
- Optimisation: replace internals of `backend/app/services/allocation.py` with OR-Tools while keeping the interface.
- Realtime: add notifications/messaging transport; current MVP uses request/response group messages.
- Production: migrate to PostgreSQL/PostGIS, managed auth, secrets, observability and CI.
