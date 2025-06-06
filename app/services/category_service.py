from typing import List
import logging
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.models.categories import Category as CategoryModel
from app.schemas.category import Category, UpdateCategory
from app.services.response_utils import ResponseUtils


class CategoryService:
  @staticmethod
  async def swap_categories_by_ids(db: AsyncSession, first_id: UUID, second_id: UUID) -> None:
    result = await db.execute(
      select(CategoryModel).filter(CategoryModel.id.in_([first_id, second_id]))
    )
    categories = result.scalars().all()

    if len(categories) != 2:
      raise ValueError("Не удалось найти обе категории для обмена")

    category_1, category_2 = categories

    pos1 = category_1.position
    pos2 = category_2.position

    category_1.position = -100
    await db.flush()
    category_2.position = pos1
    await db.flush()

    category_1.position = pos2
    await db.commit()

  @staticmethod
  async def get_category_by_id(db: AsyncSession, category_id: UUID) -> CategoryModel:
    query = select(CategoryModel).where(CategoryModel.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()
    if not category:
      raise NoResultFound(f"Category with ID {category_id} not found")
    return category

  @staticmethod
  async def get_category_by_store(db: AsyncSession, category_id: UUID) -> List[CategoryModel]:
    result = await db.execute(
      select(CategoryModel).where(CategoryModel.store_id == category_id)
    )
    return list(result.scalars().all())

  @staticmethod
  async def get_all_categories(db: AsyncSession) -> List[Category]:
    query = select(CategoryModel)
    result = await db.execute(query)
    categories = list(result.scalars().all())
    return categories

  @staticmethod
  async def create_category(db: AsyncSession, category_data: Category) -> CategoryModel:
    max_position_query = select(func.max(CategoryModel.position)).where(
      CategoryModel.store_id == category_data.store_id
    )
    result = await db.execute(max_position_query)
    max_position = result.scalar() or 0

    new_category = CategoryModel(
      name = category_data.name,
      store_id = category_data.store_id,
      is_available = category_data.is_available,
      type = category_data.type,
      position = max_position + 1,
    )
    db.add(new_category)
    try:
      await db.commit()
      await db.refresh(new_category)
    except IntegrityError:
      await db.rollback()
      raise ResponseUtils.error("Категория с такой позицией уже существует — попробуйте ещё раз")

    return new_category

  @staticmethod
  async def update_category(db: AsyncSession, category_data: UpdateCategory) -> CategoryModel:
    category = await CategoryService.get_category_by_id(db, category_data.id)

    category.name = category_data.name
    category.store_id = category_data.store_id
    category.is_available = category_data.is_available
    category.type = category_data.type

    await db.commit()
    await db.refresh(category)
    return category

  @staticmethod
  async def delete_category(db: AsyncSession, category_id: UUID) -> None:
    category = await CategoryService.get_category_by_id(db, category_id)
    await db.delete(category)
    await db.commit()