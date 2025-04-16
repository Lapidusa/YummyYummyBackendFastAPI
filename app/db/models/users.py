from sqlalchemy import Column, String, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
from enum import Enum as PyEnum

from app.db import Base

class Roles(PyEnum):
    USER = 0
    COURIER = 1
    COOK = 2
    MANAGER = 3
    ADMIN = 4

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), nullable=False, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    date_of_birth = Column(DateTime, nullable=True)
    role = Column(ENUM(Roles), default=Roles.USER)
    image_url = Column(String(255), nullable=True)
    scores = Column(Integer, default=0)