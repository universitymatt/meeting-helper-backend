from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
from typing import List
from app.db.database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

# Association table for many-to-many relationship
user_role_table = Table(
    "user_role_table",
    Base.metadata,
    Column("role", String, ForeignKey("role_table.role"), primary_key=True),
    Column("user_id", Integer, ForeignKey("user_table.id"), primary_key=True),
)

room_role_table = Table(
    "room_role_table",
    Base.metadata,
    Column("role", String, ForeignKey("role_table.role"), primary_key=True),
    Column("room_number", Integer, ForeignKey("room_table.room_number"), primary_key=True),
)

class Room(Base):
    __tablename__ = "room_table"
    
    room_number: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    capacity: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String)
    request_only: Mapped[bool] = mapped_column(Boolean, default=False)

    bookings: Mapped[List["Booking"]] = relationship(
        back_populates="room", 
        cascade="all, delete-orphan"
    )
    allowed_roles: Mapped[List["Role"]] = relationship(
        secondary=room_role_table,
        back_populates="rooms"
    )

    @property
    def allowed_role_names (self) -> List[str]:
        return [role.role for role in self.allowed_roles]


class User(Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    bookings: Mapped[List["Booking"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    roles: Mapped[List["Role"]] = relationship(
        secondary=user_role_table,
        back_populates="users"
    )
    
    @property
    def role_names(self) -> List[str]:
        return [role.role for role in self.roles]

class Booking(Base):
    __tablename__ = "booking_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=False)
    room_number: Mapped[str] = mapped_column(ForeignKey("room_table.room_number"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    room: Mapped["Room"] = relationship(back_populates="bookings")
    user: Mapped["User"] = relationship(back_populates="bookings")

class Role(Base):
    __tablename__ = "role_table"

    role: Mapped[str] = mapped_column(String, primary_key=True)

    users: Mapped[List["User"]] = relationship(
        secondary=user_role_table,
        back_populates="roles"
    )
    rooms: Mapped[List["Room"]] = relationship(
        secondary=room_role_table,
        back_populates="allowed_roles"
    )
