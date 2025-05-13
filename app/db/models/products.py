from sqlalchemy import Column, String, Float, ForeignKey, Table, Boolean, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship, declared_attr
import uuid
from enum import Enum as PyEnum, IntEnum
from app.db import Base

class Type(IntEnum):
  GROUP = 0
  CONSTRUCTOR = 1
  PIZZA = 2

class Product(Base):
  __tablename__ = "products"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String)
  description = Column(String)
  category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'))
  position = Column(Integer, nullable=False)
  type = Column(ENUM(Type), default=Type.GROUP, nullable=False)  # Тип продукта
  is_available = Column(Boolean, nullable=False, default=True)  # Доступность продукта
  variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
  replacements = relationship("ProductReplacement", back_populates="product")  # связь с заменами

  __mapper_args__ = {
    'polymorphic_identity': 'base',
    'polymorphic_on': type,
  }

class Dough(IntEnum):
  THICK_DOUGH = 0 # толстое тесто
  THIN_DOUGH = 1 # тонкое тесто

class Pizza(Product):
  __tablename__ = 'pizzas'

  id = Column(UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True)
  dough = Column(ENUM(Dough, name="dough"), default=Dough.THICK_DOUGH)

  # ingredients = relationship("PizzaIngredient", back_populates="pizza", cascade="all, delete-orphan")

  __mapper_args__ = {
    'polymorphic_identity': 'pizza',
  }

class ProductVariant(Base):
  __tablename__ = 'product_variants'
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
  size = Column(String)
  price = Column(Float)
  weight = Column(Float)
  product = relationship("Product", back_populates="variants")
  calories = Column(Float, nullable=True)  # Калории
  proteins = Column(Float, nullable=True)  # Белки
  fats = Column(Float, nullable=True)  # Жиры
  carbohydrates = Column(Float, nullable=True)  # Углеводы
  image = Column(String, nullable=True)
  is_available = Column(Boolean, nullable=False, default=True)  # Доступность варианта
# Заменяемые группы (например, «выберите 2 соуса»)

class ReplacementGroup(Base):
  __tablename__ = "replacement_groups"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String)  # например "Соусы к картошке"
  max_choices = Column(Integer, default=1)  # сколько можно выбрать

  # какие продукты входят в эту группу
  items = relationship("ReplacementItem", back_populates="group", cascade="all, delete-orphan")

  # к каким продуктам это применимо
  applicable_to = relationship("ProductReplacement", back_populates="group", cascade="all, delete-orphan")

class ReplacementItem(Base):
  __tablename__ = "replacement_items"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  group_id = Column(UUID(as_uuid=True), ForeignKey('replacement_groups.id'))
  product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))

  group = relationship("ReplacementGroup", back_populates="items")
  product = relationship("Product")

class ProductReplacement(Base):
  __tablename__ = "product_replacements"
  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))  # к какому продукту применимо
  group_id = Column(UUID(as_uuid=True), ForeignKey("replacement_groups.id"))  # какая группа выбора

  product = relationship("Product", back_populates="replacements")
  group = relationship("ReplacementGroup", back_populates="applicable_to")
