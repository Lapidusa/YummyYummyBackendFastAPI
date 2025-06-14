import uuid
from datetime import datetime
from sqlalchemy import Enum as SAEnum, UniqueConstraint, String
from sqlalchemy import Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.db.models import User, ProductVariant, Ingredient
from app.db.models.products import Dough


class CartItem(Base):
    __tablename__ = "cart_items"
    __mapper_args__ = {
        "polymorphic_identity": "cart_item",
        "polymorphic_on": "type"
    }

    type: Mapped[str] = mapped_column(String(50))
    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column( PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_variant_id: Mapped[uuid.UUID] = mapped_column( PG_UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    added_at: Mapped[datetime] = mapped_column( DateTime, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship( "User", back_populates="cart_items")
    product_variant: Mapped["ProductVariant"] = relationship( "ProductVariant")

User.cart_items = relationship( "CartItem", back_populates="user", cascade="all, delete-orphan"
)

class CartItemIngredient(Base):
    __tablename__ = "cart_item_ingredients"
    __table_args__ = (UniqueConstraint("cart_item_id", "ingredient_id", name="uq_cart_item_ingredient"),)
    id: Mapped[uuid.UUID] = mapped_column( PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_item_id: Mapped[uuid.UUID] = mapped_column( PG_UUID(as_uuid=True), ForeignKey("pizza_cart_items.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[uuid.UUID] = mapped_column( PG_UUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cart_item: Mapped["PizzaCartItem"] = relationship( "PizzaCartItem", back_populates="custom_ingredients")
    ingredient: Mapped["Ingredient"] = relationship( "Ingredient")

class PizzaCartItem(CartItem):
    __tablename__ = "pizza_cart_items"
    __mapper_args__ = {
        "polymorphic_identity": "pizza_cart_item"
    }
    id: Mapped[uuid.UUID] = mapped_column( PG_UUID(as_uuid=True), ForeignKey("cart_items.id", ondelete="CASCADE"), primary_key=True)
    dough: Mapped[Dough] = mapped_column(SAEnum(Dough, name="cart_dough", native_enum=False),default=Dough.THICK_DOUGH,nullable=False)
    custom_ingredients: Mapped[list[CartItemIngredient]] = relationship( "CartItemIngredient", back_populates="cart_item", cascade="all, delete-orphan")
