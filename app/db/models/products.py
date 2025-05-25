from sqlalchemy import String, Float, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from enum import IntEnum
from app.db import Base
from typing import List

class Type(IntEnum):
    GROUP = 0
    CONSTRUCTOR = 1
    PIZZA = 2

from sqlalchemy.orm import declared_attr

class BaseProductMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('categories.id'))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @declared_attr
    def variants(cls) -> Mapped[List["ProductVariant"]]:
        return relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

    @declared_attr
    def replacements(cls) -> Mapped[List["ProductReplacement"]]:
        return relationship("ProductReplacement", back_populates="product")

class Product(Base, BaseProductMixin):
    __tablename__ = "products"

    description: Mapped[str] = mapped_column(String)

    __mapper_args__ = {
        'polymorphic_identity': Type.GROUP,
        'polymorphic_on': BaseProductMixin.type,
    }

class Dough(IntEnum):
    THICK_DOUGH = 0
    THIN_DOUGH = 1

class Pizza(Product):
    __tablename__ = 'pizzas'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True)
    dough: Mapped[Dough] = mapped_column(ENUM(Dough, name="dough", nullable=True), default=Dough.THICK_DOUGH)

    __mapper_args__ = {
        'polymorphic_identity': Type.PIZZA,
    }

class ProductVariant(Base):
    __tablename__ = 'product_variants'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id'))

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
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('replacement_groups.id'))
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id'))

    group: Mapped["ReplacementGroup"] = relationship("ReplacementGroup", back_populates="items")
    product: Mapped["Product"] = relationship("Product")

class ProductReplacement(Base):
    __tablename__ = "product_replacements"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("replacement_groups.id"))

    product: Mapped["Product"] = relationship("Product", back_populates="replacements")
    group: Mapped["ReplacementGroup"] = relationship("ReplacementGroup", back_populates="applicable_to")
