from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.booking_controller import booking_router
from app.api.room_controller import room_router
from app.api.user_controller import user_router
from app.api.role_controller import role_router
from app.db.database import Base, engine
from app.db.seed_db import seed_data_if_needed

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_data_if_needed()
    yield


app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://universitymatt.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(booking_router)
app.include_router(room_router)
app.include_router(user_router)
app.include_router(role_router)
