# SquadMeals Backend

FastAPI backend for the SquadMeals MVP.

## MVP notes
- Uses SQLite for zero-setup local persistence (migration path to PostgreSQL/PostGIS is kept in models).
- Authentication is local JWT-based; Supabase Auth can replace the auth service behind the same interface later.
- Grocery prices are **simulated sample data** for the MVP, clearly labeled in the UI/API. Retailer API integrations can be added behind `services/pricing_provider.py`.
- Shopping allocation uses a heuristic optimizer behind `services/allocation.py`; Google OR-Tools can be plugged in later.
- Geo discovery uses lat/lng + Haversine distance; PostGIS and map providers can be integrated later.
