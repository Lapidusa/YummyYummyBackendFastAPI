from enum import IntEnum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.product import IngredientResponse


class TypeCategory(IntEnum):
  GROUP = 0
  PIZZA = 1
  CONSTRUCTOR = 2

class Dough(IntEnum):
  THICK_DOUGH = 0
  THIN_DOUGH = 1

class City(BaseModel):
    id: UUID
    name: str
    stores: list["Store"]
    model_config = {"from_attributes": True}

class Store(BaseModel):
    id: UUID
    categories: list["Category"]

    model_config = {"from_attributes": True}

class Category(BaseModel):
    id: UUID
    name: str
    products: list["Product | Pizza"]
    is_available: bool
    type: TypeCategory
    position: int
    model_config = ConfigDict(from_attributes=True)

class Product(BaseModel):
    id: UUID
    name: str
    type: int
    position: int
    description: str
    is_available: bool
    variants: list["ProductVariant"] | None = None

    model_config = ConfigDict(from_attributes=True)

class Pizza(Product):
    id: UUID
    ingredients: list[IngredientResponse] = []
    dough: Dough
    model_config = ConfigDict(from_attributes=True)

class ProductVariant(BaseModel):
    id: UUID
    size: str
    price: float
    weight: float
    calories: float
    proteins:float
    fats:float
    carbohydrates: float
    image: str
    is_available: bool
    model_config = ConfigDict(from_attributes=True)

class Ingredient(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

class PizzaIngredient(BaseModel):
    ingredient: Ingredient
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)

class CreateCity(City):
  pass

class UpdateCity(City):
  id: UUID = Field(..., description="Уникальный идентификатор города")
  pass
