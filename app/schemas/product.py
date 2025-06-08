from enum import IntEnum

from pydantic import BaseModel, model_validator
from typing import List, Optional, Literal
from uuid import UUID
from app.db.models.products import Dough

class TypeProduct(IntEnum):
  GROUP = 0
  CONSTRUCTOR = 1
  PIZZA = 2

class IngredientResponse(BaseModel):
  id: UUID
  name: str
  image: Optional[str]
  overlay_image: Optional[str]
  price: int
  is_deleted: bool

  model_config = {"from_attributes": True}

class ProductVariantResponse(BaseModel):
  id: UUID
  size: str
  price: float
  weight: float
  calories: Optional[float]
  proteins: Optional[float]
  fats: Optional[float]
  carbohydrates: Optional[float]
  image: Optional[str]
  is_available: bool

  model_config = {"from_attributes": True}

class ProductResponse(BaseModel):
  id: UUID
  name: str
  description: Optional[str]
  category_id: UUID
  position: int
  type: TypeProduct
  is_available: bool

  variants: List[ProductVariantResponse] = []
  ingredients: List[IngredientResponse] = []

  model_config = {"from_attributes": True}

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

class ProductBase(BaseModel):
  name: str
  category_id: UUID
  is_available: bool = True
  variants: List[ProductVariantCreate]
  position: int

  model_config = {
    "from_attributes": True,
    "extra": "forbid",
  }

  @model_validator(mode="after")
  def check_variants(self) -> "ProductBase":
    if not self.variants:
      raise ValueError("У продукта должен быть хотя бы один вариант")
    return self

class IngredientInPizza(BaseModel):
  ingredient_id: UUID
  is_deleted: Optional[bool] = False

class PizzaCreate(ProductBase):
  type: Literal[TypeProduct.PIZZA]
  description: Optional[str] = None
  dough: Dough
  ingredients: List[IngredientInPizza]

class ProductCreate(ProductBase):
  type: TypeProduct
  description: Optional[str] = None

class PizzaUpdate(PizzaCreate):
  id: UUID

class ProductUpdate(ProductCreate):
  id: UUID