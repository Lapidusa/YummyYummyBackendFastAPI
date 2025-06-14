from datetime import datetime
from enum import IntEnum
from uuid import UUID
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from app.db.models.orders import PaymentMethod
from app.db.models.products import Dough


class OrderStatus(IntEnum):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    CANCELLED = 3

class OrderItemIngredientCreate(BaseModel):
    ingredient_id: UUID
    quantity: int
    is_removed: bool

class OrderAddressCreate(BaseModel):
    street: str
    house: str
    apartment: Optional[str]
    comment: Optional[str]

class OrderItemCreate(BaseModel):
    product_variant_id: UUID
    quantity: int
    type: Literal["simple", "pizza"]
    dough: Optional[Dough] = None
    added_ingredients: List[OrderItemIngredientCreate] = []
    removed_ingredients: List[OrderItemIngredientCreate] = []

class OrderCreate(BaseModel):
    is_pickup: bool
    store_id: Optional[UUID]
    payment_method: PaymentMethod
    address: Optional[OrderAddressCreate]
    items: List[OrderItemCreate]

class OrderAddressRead(OrderAddressCreate):
    pass
class OrderItemIngredientRead(OrderItemIngredientCreate):
    ingredient_name: Optional[str]

class OrderStatusUpdate(BaseModel):
    id_order: UUID
    status: OrderStatus

class OrderItemRead(BaseModel):
    product_variant_id: UUID
    quantity: int
    price_per_item: float
    product_name: str
    variant_size: str
    type: str
    dough: Optional[Dough]
    added_ingredients: List[OrderItemIngredientRead]
    removed_ingredients: List[OrderItemIngredientRead]

class OrderRead(BaseModel):
    id: UUID
    user_id: UUID
    total_price: float
    is_pickup: bool
    store_id: Optional[UUID]
    payment_method: PaymentMethod
    status: int
    created_at: datetime
    address: Optional[OrderAddressRead]
    items: List[OrderItemRead]

