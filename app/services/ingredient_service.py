from app.db.models.ingredients import Ingredient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

class IngredientService:
  @staticmethod
  async def get_all(db: AsyncSession):
    result = await db.execute(select(Ingredient))
    return result.scalars().all()

  @staticmethod
  async def get_by_id(ingredient_id: UUID, db: AsyncSession):
    result = await db.execute(
      select(Ingredient).where(Ingredient.id == ingredient_id)
    )
    return result.scalar_one_or_none()

  @staticmethod
  async def create(ingredient_data, db: AsyncSession):
    ingredient = Ingredient(**ingredient_data)
    db.add(ingredient)
    await db.commit()
    await db.refresh(ingredient)
    return ingredient

  @staticmethod
  async def update(ingredient_id: UUID, update_data, db: AsyncSession):
    result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
    ingredient = result.scalar_one_or_none()
    for field, value in update_data.items():
      setattr(ingredient, field, value)
    await db.commit()
    await db.refresh(ingredient)
    return ingredient

  @staticmethod
  async def delete(ingredient_id: UUID, db: AsyncSession):
    result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
    ingredient = result.scalar_one_or_none()
    if not ingredient:
      return None
    await db.commit()
    return ingredient
