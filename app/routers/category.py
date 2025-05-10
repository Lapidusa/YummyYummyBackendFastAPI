from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Header
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityMiddleware
from app.db import get_db
from app.schemas.category import SwapCategory, CreateCategory, UpdateCategory
from app.services.category_service import CategoryService
from app.services.response_utils import ResponseUtils

router = APIRouter()

@router.get("/get-category/{category_id}/")
async def get_category_endpoint(category_id: UUID, db: AsyncSession = Depends(get_db)):
  try:
    category = await CategoryService.get_category_by_id(db, category_id)
    return ResponseUtils.success(category=category)
  except NoResultFound:
    return ResponseUtils.error(message=f"Нет найденного категории с айди {category_id}")

@router.get("/all-categories/")
async def get_all_categories_endpoint(db: AsyncSession = Depends(get_db)):
  categories = await CategoryService.get_all_categories(db)
  return ResponseUtils.success(categories=categories)

@router.get("/get-category-by-store/{store_id}")
async def get_category_by_store_endpoint(store_id: UUID, db: AsyncSession = Depends(get_db)):
  categories = await CategoryService.get_category_by_store(db, store_id)
  return ResponseUtils.success(categories=categories)

@router.post("/swap-position/")
async def swap_categories_endpoint(
    swap_data: SwapCategory,
    db: AsyncSession = Depends(get_db),
    token: str = Header(None)
):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  await CategoryService.swap_categories_by_ids(db, swap_data.first_category, swap_data.second_category)
  return ResponseUtils.success(message="Позиции поменялись")

@router.post('/create-category/')
async def create_category_endpoint(
  category_data: CreateCategory,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None)
):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)
  new_category = await CategoryService.create_category(db, category_data)
  return ResponseUtils.success(category=new_category)

@router.put("/{category_id}")
async def update_category_endpoint(
    category_data: UpdateCategory,
    db: AsyncSession = Depends(get_db),
    token: str = Header(None)
):
  if token is None:
    raise ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)
  updated_category = await CategoryService.update_category(db, category_data)
  return ResponseUtils.success(category=updated_category)

@router.delete("/{category_id}")
async def delete_category_endpoint(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: str = Header(None)
):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)
  try:
    await CategoryService.delete_category(db, category_id)
    return ResponseUtils.success(message="Категория удалена")
  except NoResultFound:
    return ResponseUtils.error(message="Категория не найдена")