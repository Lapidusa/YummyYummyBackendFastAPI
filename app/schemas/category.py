from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum
from typing import Optional


class TypeCategory(str, Enum):
    GROUP = "group"
    PIZZA = "pizza"
    CONSTRUCTOR = "constructor"

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
  pass

class SwapCategory(BaseModel):
  first_category: UUID
  second_category: UUID