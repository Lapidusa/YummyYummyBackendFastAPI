from typing import List

from pydantic import BaseModel, Field
from uuid import UUID
from enum import IntEnum

from app.db.models import Product
from app.schemas.product import ProductResponse

class TypeCategory(IntEnum):
  GROUP = 0
  PIZZA = 1
  CONSTRUCTOR = 2

class Category(BaseModel):
  name: str = Field(..., description="Название категории")
  store_id: UUID = Field(..., description="ID магазина, к которому привязана категория")
  is_available: bool = Field(..., description="Доступна ли категория")
  type: TypeCategory = Field(..., description="Тип категории (group, pizza, constructor)")
  class Config:
      from_attributes = True

class CreateCategory(Category):
  pass

class UpdateCategory(Category):
  id: UUID = Field(..., description="Уникальный идентификатор категории")

class SwapCategory(BaseModel):
  first_category: UUID
  second_category: UUID