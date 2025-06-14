"""FastAPI application entry point for the room booking system"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.booking_controller import booking_router
from app.api.room_controller import room_router
from app.api.user_controller import user_router
from app.api.role_controller import role_router
from app.db.database import Base, engine

logging.basicConfig(level=logging.INFO)

# Create tables on startup
Base.metadata.create_all(bind=engine)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://universitymatt.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(booking_router)
app.include_router(room_router)
app.include_router(user_router)
app.include_router(role_router)
