import uuid
from datetime import datetime
from enum import IntEnum
from sqlalchemy import Enum as PgEnum
from sqlalchemy import Float, UUID, DateTime, func, Boolean, ForeignKey, String, Integer
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db import Base


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

class OrderItem(Base):
  __tablename__ = "order_items"

  id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"))
  product_variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id"))

  quantity: Mapped[int] = mapped_column(Integer)
  price_per_item: Mapped[float] = mapped_column(Float)

  order = relationship("Order", back_populates="items")
  product_variant = relationship("ProductVariant")

class Order(Base):
  __tablename__ = "orders"

  id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
  total_price: Mapped[float] = mapped_column(Float)
  is_pickup: Mapped[bool] = mapped_column(Boolean, default=False)
  created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
  status: Mapped[OrderStatus] = mapped_column(ENUM(OrderStatus), default=OrderStatus.PENDING)

  user = relationship("User", back_populates="orders")
  items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
  address = relationship("OrderAddress", uselist=False, back_populates="order")

  payment_method: Mapped[PaymentMethod] = mapped_column(
    PgEnum(PaymentMethod, name="payment_method_enum"),
    nullable=False
  )