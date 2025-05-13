from pydantic import BaseModel, model_validator, Field
from typing import List, Optional
from uuid import UUID

from app.db.models.products import Type

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

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: UUID
    is_available: bool = True
    type: Type
    variants: List[ProductVariantCreate] = []
    replacements: List[ProductReplacementCreate] = []

    @model_validator(mode="after")
    def check_variants(self) -> "ProductCreate":
      if not self.variants:
        raise ValueError("У продукта должен быть хотя бы один вариант")
      return self
