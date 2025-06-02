import uuid
from sqlalchemy.dialects.postgresql import ENUM, UUID as PGUUID
from enum import IntEnum
from sqlalchemy import Column, String, ForeignKey, Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class TypeCategory(IntEnum):
  GROUP = 0
  PIZZA = 1
  CONSTRUCTOR = 2

class Category(Base):
  __tablename__ = 'categories'

  id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String(255), nullable=False)
  store_id = Column(PGUUID(as_uuid=True), ForeignKey('stores.id'))
  is_available = Column(Boolean, nullable=False, default=True)
  type = Column(ENUM(TypeCategory), default=TypeCategory.GROUP, nullable=False)
  position = Column(Integer, nullable=False)
  store = relationship("Store", back_populates="categories")
  products = relationship(
    "Product",
    back_populates="category"
  )
  __table_args__ = (
    UniqueConstraint("store_id", "position", name="uix_store_position"),
  )
