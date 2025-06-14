from sqlalchemy import String, Float, ForeignKey, Boolean, Integer, Enum as PGEnum
from uuid import UUID
from sqlalchemy.dialects.postgresql import ENUM, UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from uuid import UUID as UUID_PY
from enum import IntEnum
from app.db import Base
from typing import List

from app.db.models.categories import Category


class PizzaIngredient(Base):
  __tablename__ = "pizza_ingredients"

  pizza_id: Mapped[UUID_PY] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pizzas.id", ondelete="CASCADE"), primary_key=True)
  ingredient_id: Mapped[UUID_PY] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ingredients.id", ondelete="RESTRICT"), primary_key=True)

  is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

  pizza = relationship("Pizza", back_populates="pizza_ingredients")
  ingredient = relationship("Ingredient", back_populates="pizza_ingredients")


class Type(IntEnum):
  GROUP = 0
  CONSTRUCTOR = 1
  PIZZA = 2

from sqlalchemy.orm import declared_attr

class BaseProductMixin:
  id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name: Mapped[str] = mapped_column(String)
  category_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('categories.id'))
  position: Mapped[int] = mapped_column(Integer, nullable=False)
  type: Mapped[int] = mapped_column(Integer, nullable=False)
  is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class Product(Base, BaseProductMixin):
  __tablename__ = "products"

  description: Mapped[str] = mapped_column(String)
  category: Mapped["Category"] = relationship("Category", back_populates="products")
  variants: Mapped[List["ProductVariant"]] = relationship(
    "ProductVariant", back_populates="product", cascade="all, delete-orphan"
  )

  replacements: Mapped[List["ProductReplacement"]] = relationship(
    "ProductReplacement", back_populates="product", cascade="all, delete-orphan"
  )

  __mapper_args__ = {
    'polymorphic_identity': Type.GROUP,
    'polymorphic_on': BaseProductMixin.type,
  }

class Dough(IntEnum):
  THICK_DOUGH = 0
  THIN_DOUGH = 1


class Pizza(Product):
  __tablename__ = "pizzas"

  id: Mapped[UUID] = mapped_column(
    PGUUID(as_uuid=True),
    ForeignKey("products.id"),
    primary_key=True,
  )
  dough: Mapped[Dough] = mapped_column(
    PGEnum(Dough, name="dough", nullable=True),
    default=Dough.THICK_DOUGH,
  )

  pizza_ingredients = relationship(
    "PizzaIngredient",
    back_populates="pizza",
    cascade="all, delete-orphan",
    passive_deletes=True,
  )

  @property
  def ingredients(self) -> list["IngredientResponse"]:
    from app.schemas.product import IngredientResponse

    return [
      IngredientResponse(
        id=pi.ingredient.id,
        name=pi.ingredient.name,
        image=pi.ingredient.image,
        overlay_image=pi.ingredient.overlay_image,
        price=pi.ingredient.price,
        is_deleted=pi.is_deleted,
      )
      for pi in self.pizza_ingredients
      if pi.ingredient
    ]

  variants: Mapped[list["ProductVariant"]] = relationship(
    "ProductVariant",
    back_populates="product",
    cascade="all, delete-orphan",
  )

  __mapper_args__ = {
    "polymorphic_identity": Type.PIZZA,
  }

class ProductVariant(Base):
  __tablename__ = 'product_variants'

  id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  product_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('products.id'))

  size: Mapped[str] = mapped_column(String)
  price: Mapped[float] = mapped_column(Float)
  weight: Mapped[float] = mapped_column(Float)

  calories: Mapped[float | None] = mapped_column(Float, nullable=True)
  proteins: Mapped[float | None] = mapped_column(Float, nullable=True)
  fats: Mapped[float | None] = mapped_column(Float, nullable=True)
  carbohydrates: Mapped[float | None] = mapped_column(Float, nullable=True)

  image: Mapped[str | None] = mapped_column(String, nullable=True)
  is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

  product: Mapped["Product"] = relationship("Product", back_populates="variants")

class ReplacementGroup(Base):
  __tablename__ = "replacement_groups"
  id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name: Mapped[str] = mapped_column(String)
  max_choices: Mapped[int] = mapped_column(Integer, default=1)

  items: Mapped[List["ReplacementItem"]] = relationship(
    "ReplacementItem", back_populates="group", cascade="all, delete-orphan"
  )
  applicable_to: Mapped[List["ProductReplacement"]] = relationship(
    "ProductReplacement", back_populates="group", cascade="all, delete-orphan"
  )

class ReplacementItem(Base):
  __tablename__ = "replacement_items"
  id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  group_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('replacement_groups.id'))
  product_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey('products.id'))

  group: Mapped["ReplacementGroup"] = relationship("ReplacementGroup", back_populates="items")
  product: Mapped["Product"] = relationship("Product")

class ProductReplacement(Base):
  __tablename__ = "product_replacements"
  id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  product_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id"))
  group_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("replacement_groups.id"))

  product: Mapped["Product"] = relationship("Product", back_populates="replacements")
  group: Mapped["ReplacementGroup"] = relationship("ReplacementGroup", back_populates="applicable_to")
