from sqlalchemy import Column, String, DateTime, Time, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
# from app.db.models.category import store_categories
from app.db import Base
from geoalchemy2 import Geometry

class Store(Base):
  __tablename__ = "stores"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Уникальный идентификатор магазина
  address = Column(String(500), nullable=False)  # Адрес магазина
  start_working_hours = Column(Time(timezone=False), nullable=False)  # Начало рабочего времени
  end_working_hours = Column(Time(timezone=False), nullable=False)  # Конец рабочего времени
  start_delivery_time = Column(Time(timezone=False), nullable=False)  # Начало времени доставки
  end_delivery_time = Column(Time(timezone=False), nullable=False)  # Конец времени доставки
  phone_number = Column(String(15), nullable=False, unique=True)  # Номер телефона магазина
  min_order_price = Column(Integer, nullable=False, default=0)  # Минимальная сумма заказа
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # Дата создания записи
  updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))  # Дата обновления записи
  area = Column(Geometry('POLYGON'), nullable=False)  # Полигон
  point = Column(Geometry('POINT'), nullable=False)  # Точка магазина
  city_id = Column(UUID(as_uuid=True), ForeignKey('cities.id'), nullable=False)  # Связь с городом
  city = relationship("City", back_populates="stores")  # Обратная связь с моделью City
  # categories = relationship("Category", secondary=store_categories, back_populates="stores")