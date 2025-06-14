import uuid
from datetime import datetime
from decimal import Decimal
from enum import IntEnum
from sqlalchemy import Enum as PgEnum, Numeric
from sqlalchemy import Float, UUID, DateTime, Boolean, ForeignKey, String, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db import Base
from app.db.models.products import Dough

class OrderStatus(IntEnum):
  PENDING = 0
  IN_PROGRESS = 1
  COMPLETED = 2
  CANCELLED = 3

class PaymentMethod(IntEnum):
  CASH = 0
  ELECTRONIC = 1

class OrderAddress(Base):
  __tablename__ = "order_addresses"

  id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"))
  street: Mapped[str] = mapped_column(String)
  house: Mapped[str] = mapped_column(String)
  apartment: Mapped[str | None] = mapped_column(String, nullable=True)
  comment: Mapped[str | None] = mapped_column(String, nullable=True)

  order = relationship("Order", back_populates="address")

class Order(Base):
  __tablename__ = "orders"
  id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
  total_price: Mapped[float] = mapped_column(Float, default=0.0)
  is_pickup: Mapped[bool] = mapped_column(Boolean, default=False)
  store_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
  status: Mapped[OrderStatus] = mapped_column(PgEnum(OrderStatus), default=OrderStatus.PENDING)
  payment_method: Mapped[PaymentMethod] = mapped_column(PgEnum(PaymentMethod, name="payment_method_enum"), nullable=False)

  user = relationship("User", back_populates="orders")
  address = relationship("OrderAddress", uselist=False, back_populates="order")
  items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
  __tablename__ = "order_items"
  id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  order_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("orders.id"))

  product_variant_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("product_variants.id"))
  quantity: Mapped[int] = mapped_column(Integer)
  price_per_item: Mapped[Decimal] = mapped_column(Numeric(10, 2))
  product_name: Mapped[str] = mapped_column(String)

  variant_size: Mapped[str] = mapped_column(String)
  type: Mapped[str] = mapped_column(String)
  dough: Mapped[Dough | None] = mapped_column(PgEnum(Dough), nullable=True)

  order = relationship("Order", back_populates="items")
  custom_ingredients = relationship(
    "OrderItemIngredient",
    back_populates="order_item",
    cascade="all, delete-orphan"
  )


class OrderItemIngredient(Base):
  __tablename__ = "order_item_ingredients"
  id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  order_item_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True),
                                                   ForeignKey("order_items.id", ondelete="CASCADE"))
  ingredient_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("ingredients.id"))
  quantity: Mapped[int] = mapped_column(Integer, default=1)
  is_removed: Mapped[bool] = mapped_column(Boolean, default=False)

  order_item = relationship("OrderItem", back_populates="custom_ingredients")
  ingredient = relationship("Ingredient")