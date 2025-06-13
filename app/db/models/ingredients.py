import uuid
from uuid import UUID as UUID_PY
from sqlalchemy import String, UUID, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class Ingredient(Base):
  __tablename__ = "ingredients"

  id: Mapped[UUID_PY] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
    nullable=False,
  )
  name: Mapped[str] = mapped_column(String, nullable=False)
  image: Mapped[str | None] = mapped_column(String)
  overlay_image: Mapped[str] = mapped_column(String)
  price: Mapped[int] = mapped_column(Integer)
  pizza_ingredients = relationship("PizzaIngredient", back_populates="ingredient",cascade="all, delete-orphan", passive_deletes=True)
