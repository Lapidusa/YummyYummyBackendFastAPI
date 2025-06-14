from typing import Literal, List, Union, Annotated

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from app.db.models.products import Dough
from app.schemas.ingredient import IngredientBase, IngredientOut
from app.schemas.product import ProductVariantOut


class AddedIngredient(BaseModel):
    ingredient_id: UUID
    quantity: int

class RemovedIngredient(AddedIngredient):
    pass

class SimpleCartItem(BaseModel):
    type: Literal["simple"]
    product_variant_id: UUID
    quantity: int = 1

    class Config:
        extra = "forbid"

class PizzaCartItem(BaseModel):
    type: Literal["pizza"]
    product_variant_id: UUID
    quantity: int = 1
    dough: Dough
    added_ingredients: list[AddedIngredient] = []
    removed_ingredients: list[RemovedIngredient] = []
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )

CartItemCreate = Annotated[
    Union[SimpleCartItem, PizzaCartItem],
    Field(discriminator='type')
]

class CartItemIngredientOut(BaseModel):
    ingredient: IngredientOut
    quantity: int

    model_config = ConfigDict(
        from_attributes=True,

    )

class SimpleCartItemOut(BaseModel):
    id: UUID
    quantity: int
    price: int
    name: str
    type: Literal["simple"]
    variant: ProductVariantOut

    model_config = ConfigDict(
        from_attributes=True,

    )

class PizzaCartItemOut(BaseModel):
    id: UUID
    quantity: int
    dough: Dough
    price: int
    name: str
    type: Literal["pizza"]
    added_ingredients: list[CartItemIngredientOut]
    removed_ingredients: list[CartItemIngredientOut]
    variant: ProductVariantOut

    model_config = ConfigDict(
        from_attributes=True,
    )