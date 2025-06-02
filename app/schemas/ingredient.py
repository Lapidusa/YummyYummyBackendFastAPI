# app/schemas/ingredient.py
from typing import Optional

from pydantic import BaseModel, UUID4

class IngredientBase(BaseModel):
    name: str
    image: Optional[str]
    overlay_image: Optional[str]
    price: int

    model_config = {"from_attributes": True}

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(IngredientBase):
    pass

class IngredientOut(IngredientBase):
    id: UUID4

