from sqlalchemy import Column, String, DateTime, Time, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.db import Base
from geoalchemy2 import Geometry

class Store(Base):
  __tablename__ = "stores"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  address = Column(String(500), nullable=False)
  start_working_hours = Column(Time(timezone=False), nullable=False)
  end_working_hours = Column(Time(timezone=False), nullable=False)
  start_delivery_time = Column(Time(timezone=False), nullable=False)
  end_delivery_time = Column(Time(timezone=False), nullable=False)
  phone_number = Column(String(15), nullable=False, unique=True)
  min_order_price = Column(Integer, nullable=False, default=0)
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
  updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
  area = Column(Geometry('POLYGON'), nullable=False)
  point = Column(Geometry('POINT'), nullable=False)
  city_id = Column(UUID(as_uuid=True), ForeignKey('cities.id'), nullable=False)
  city = relationship("City", back_populates="stores")
  categories = relationship("Category", back_populates="store", cascade="all, delete-orphan")
