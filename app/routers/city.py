from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends, Header
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityMiddleware
from app.db import get_db
from app.schemas.city import CreateCity, UpdateCity
from app.services.response_utils import ResponseUtils
from app.services.city_service import CityService
router = APIRouter()

@router.get("/{city_id}")
async def get_city(city_id: UUID, db: AsyncSession = Depends(get_db)):
  try:
    city = await CityService.get_city_by_id(db, city_id)
    return {"city": city}
  except NoResultFound:
    raise ResponseUtils.error(message=f"Нет найденного города с id {city_id}")

@router.get("/all-cities/")
async def get_all_city_endpoint(db: AsyncSession = Depends(get_db)):
  categories = await CityService.get_all_cities(db)
  return ResponseUtils.success(data=categories)

@router.post("/")
async def create_city(
  city_data: CreateCity,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None)
):
  if token is None:
    raise ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)
  try:
    new_category = await CityService.create_city(db, city_data)
    return ResponseUtils.success(data=new_category, message="Категория создана")
  except Exception as e:
    raise ResponseUtils.error(message=str(e))

@router.put("/")
async def update_city(
  category_data: UpdateCity,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None)
):
  if token is None:
    raise ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)
  try:
    updated_city = await CityService.update_city(db, category_data)
    return ResponseUtils.success(data=updated_city, message="Город успешно изменен")
  except Exception as e:
    raise ResponseUtils.error(message=str(e))

@router.delete("/{city_id}")
async def delete_category_endpoint(
  city_id: UUID,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None)
):
  if token is None:
    raise ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  try:
    await CityService.delete_city(db, city_id)
    return ResponseUtils.success(message="Город удален")
  except NoResultFound:
    raise ResponseUtils.error(message=f"Город не найден с Id:{city_id}")