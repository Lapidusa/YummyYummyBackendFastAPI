from fastapi import Depends, APIRouter
from fastapi.params import Header
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.security import SecurityMiddleware
from app.db import get_db
from app.services.response_utils import ResponseUtils
from app.schemas.store import UpdateStore, CreateStore, StoreResponse
from app.services.store_service import StoreService
router = APIRouter()

@router.get("/get-store/{store_id}/")
async def get_store_endpoint(store_id: UUID, db: AsyncSession = Depends(get_db)):
  try:
    store = await StoreService.get_store_by_id(db, store_id)
    await StoreService.convert_geometry(store)
    response_data = StoreResponse.model_validate(store)
    return ResponseUtils.success(store=response_data.model_dump())
  except NoResultFound:
    return ResponseUtils.error(message="Нет найденного магазина")

@router.get("/get-stores-by-city/{city_id}/")
async def get_stores_by_city_endpoint(
  city_id: UUID,
  db: AsyncSession = Depends(get_db)
):
  stores = await StoreService.get_stores_by_city(db, city_id)
  for store in stores:
    await StoreService.convert_geometry(store)
  response_data = [StoreResponse.model_validate(store).model_dump() for store in stores]
  return ResponseUtils.success(stores=response_data)

@router.get("/all-stores/")
async def get_all_stores_endpoint(db: AsyncSession = Depends(get_db)):
  stores = await StoreService.get_all_stores(db)
  for store in stores:
    await StoreService.convert_geometry(store)
  response_data = [StoreResponse.model_validate(store).model_dump() for store in stores]
  return ResponseUtils.success(stores=response_data)

@router.post("/create-store/")
async def create_store_endpoint(
  store_data: CreateStore,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None)
):
  await SecurityMiddleware.is_admin(token, db)

  try:
    new_store = await StoreService.create_store(db, store_data)
    await StoreService.convert_geometry(new_store)
    return ResponseUtils.success(store=StoreResponse.model_validate(new_store).model_dump())

  except IntegrityError as e:
    if "stores_phone_number_key" in str(e.orig):
      return ResponseUtils.error(message="Магазин с таким номером телефона уже существует.")
    return ResponseUtils.error(message="Произошла ошибка при создании магазина.")
  except Exception as e:
    return ResponseUtils.error(message=str(e))

@router.put("/{store_id}/")
async def update_store_endpoint(
  store_data: UpdateStore,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None)
):
  await SecurityMiddleware.is_admin(token, db)

  try:
    updated_store = await StoreService.update_store(db, store_data)
    await StoreService.convert_geometry(updated_store)
    response_data = StoreResponse.model_validate(updated_store)
    return ResponseUtils.success(store=response_data.model_dump())

  except NoResultFound:
    raise ResponseUtils.error(message="Магазин не найден")

  except IntegrityError as e:
    if "stores_phone_number_key" in str(e.orig):
      return ResponseUtils.error(message="Магазин с таким номером телефона уже существует.")
    return ResponseUtils.error(message="Произошла ошибка при изменении магазина.")
  except Exception as e:
    return ResponseUtils.error(message=str(e))

@router.delete("/{store_id}/")
async def delete_store_endpoint(
  store_id: UUID,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None)
):
  await SecurityMiddleware.is_admin(token, db)

  try:
    await StoreService.delete_store(db, store_id)
    return ResponseUtils.success(message="Магазин удален")
  except NoResultFound:
    return ResponseUtils.error(message="Магазин не найден")