from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import time, datetime
from uuid import UUID

from app.schemas.category import Category

class Store(BaseModel):
  address: str = Field(..., description="Адрес магазина")
  start_working_hours: time = Field(..., description="Начало рабочего времени")
  end_working_hours: time = Field(..., description="Конец рабочего времени")
  start_delivery_time: time = Field(..., description="Начало времени доставки")
  end_delivery_time: time = Field(..., description="Конец времени доставки")
  phone_number: str = Field(..., description="Номер телефона магазина")
  min_order_price: int = Field(..., description="Минимальная сумма для заказа")
  city_id: UUID
  area: List[List[float]]
  point: List[float]
  created_at:datetime
  updated_at:datetime

  class Config:
    from_attributes = True

class StoreResponse(Store):
  id: UUID = Field(..., description="Уникальный идентификатор магазина")

  class Config:
    model_config = ConfigDict(from_attributes=True)

class CreateStore(Store):
  pass

class UpdateStore(Store):
  id: UUID