from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, cooking, groups, plans, recipes, shopping, stores, users
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.seed.data import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(plans.router, prefix="/api")
app.include_router(stores.router, prefix="/api")
app.include_router(shopping.router, prefix="/api")
app.include_router(cooking.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name, "note": "MVP uses simulated grocery prices where indicated."}
