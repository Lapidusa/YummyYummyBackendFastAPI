# app/schemas/ingredient.py
from typing import Optional

from pydantic import BaseModel, UUID4

class IngredientBase(BaseModel):
    name: str
    image: Optional[str] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(IngredientBase):
    pass

class IngredientOut(IngredientBase):
    id: UUID4
    is_deleted: bool
