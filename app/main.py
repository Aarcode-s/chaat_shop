from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables, seed_menu_items
from app.routers.auth import router as auth_router
from app.routers.contact import router as contact_router
from app.routers.menu import router as menu_router
from app.routers.orders import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Prepare the local database before serving requests."""
    create_db_and_tables()
    seed_menu_items()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Chaat Corner API",
    description="Ordering API for Chaat Corner.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(orders_router)
app.include_router(contact_router)


@app.get("/")
def root():
    """Provide a lightweight health response for local and hosted checks."""
    return {"message": "Chaat Corner API is running"}