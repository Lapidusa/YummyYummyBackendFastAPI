from enum import Enum as PyEnum, IntEnum

from pydantic import BaseModel, model_validator, Field
from typing import List, Optional, Literal
from uuid import UUID
import re
from app.db.models.products import Type, Dough

class TypeProduct(IntEnum):
  GROUP = 0
  CONSTRUCTOR = 1
  PIZZA = 2

class PizzaSize(PyEnum):
  S = 0
  M = 1
  L = 2

class ProductVariantCreate(BaseModel):
    size: str
    price: float
    weight: float
    calories: Optional[float] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbohydrates: Optional[float] = None
    is_available: bool = True
    image: Optional[str] = None

class ReplacementItemCreate(BaseModel):
    product_id: UUID

class ReplacementGroupCreate(BaseModel):
    name: str
    max_choices: int = 1
    items: List[ReplacementItemCreate]

class ProductReplacementCreate(BaseModel):
    group: ReplacementGroupCreate

class ProductBase(BaseModel):
  name: str
  category_id: UUID
  is_available: bool = True
  variants: List[ProductVariantCreate]
  replacements: List[ProductReplacementCreate] = []

  @model_validator(mode="after")
  def check_variants(self) -> "ProductBase":
    if not self.variants:
      raise ValueError("У продукта должен быть хотя бы один вариант")
    return self

class IngredientInPizza(BaseModel):
  ingredient_id: int
  is_deleted: Optional[bool] = False

class PizzaCreate(ProductBase):
  type: Literal[TypeProduct.PIZZA]
  description: Optional[str] = None
  dough: Dough
  ingredients: List[IngredientInPizza]

class ProductCreate(ProductBase):
  type: TypeProduct  # обычный
  description: Optional[str] = None

class PizzaUpdate(PizzaCreate):
  pass

class ProductUpdate(ProductCreate):
  pass