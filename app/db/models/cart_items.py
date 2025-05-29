import uuid
from datetime import datetime

from sqlalchemy import UUID, ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.db.models import User


class CartItem(Base):
  __tablename__ = "cart_items"

  id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
  product_variant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id"))

  quantity: Mapped[int] = mapped_column(Integer, default=1)
  added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

  user = relationship("User", back_populates="cart_items")
  product_variant = relationship("ProductVariant")


User.cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
