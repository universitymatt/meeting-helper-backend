from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime
from typing import List
from app.db.database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Room(Base):
    __tablename__ = "room_table"
    
    room_number: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    capacity: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String)
    request_only: Mapped[bool] = mapped_column(Boolean, default=False)

    bookings: Mapped[List["Booking"]] = relationship(back_populates="room")

class User(Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    bookings: Mapped[List["Booking"]] = relationship(back_populates="user") 

class Booking(Base):
    __tablename__ = "booking_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    room_number: Mapped[str] = mapped_column(ForeignKey("room_table.room_number"))
    start_time: Mapped[str] = mapped_column(DateTime, nullable=False)
    end_time = mapped_column(DateTime, nullable=False)
    
    room: Mapped["Room"] = relationship(back_populates="bookings")
    user: Mapped["User"] = relationship(back_populates="bookings")