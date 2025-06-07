from typing import List

from sqlalchemy import Column, String, DateTime, Integer, func, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM, UUID as PGUUID
import uuid
from enum import IntEnum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.db.models.orders import Order

class Roles(IntEnum):
    USER = 0
    COURIER = 1
    COOK = 2
    MANAGER = 3
    ADMIN = 4

class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), nullable=False, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    date_of_birth = Column(DateTime, nullable=True)
    role = Column(ENUM(Roles), default=Roles.USER)
    image_url = Column(String(255), nullable=True)
    scores = Column(Integer, default=0)
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class UserAddress(Base):
    __tablename__ = "user_addresses"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    street: Mapped[str] = mapped_column(String)
    house: Mapped[str] = mapped_column(String)
    apartment: Mapped[str | None] = mapped_column(String, nullable=True)
    label: Mapped[str | None] = mapped_column(String, nullable=True)

    user = relationship("User", back_populates="addresses")

User.addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
