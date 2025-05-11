from datetime import datetime
from uuid import UUID
from typing import List, cast
from shapely.geometry import Point, Polygon
from geoalchemy2.shape import from_shape
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.models.stores import Store
from app.db.models.stores import Store as StoreModel
from app.schemas.store import CreateStore, UpdateStore
from shapely.wkb import loads as load_wkb
from shapely.wkb import dumps as to_wkb
from app.services.response_utils import ResponseUtils


class StoreService:
  @staticmethod
  async def validate_geometry(db: AsyncSession, point_data: bytes, area_data: bytes, store_id: UUID = None):
    point_geom = load_wkb(point_data)
    area_geom = load_wkb(area_data)

    # Проверка: точка внутри полигона
    if not area_geom.contains(point_geom):
      return ResponseUtils.error(message="Локация магазина должна находиться внутри границы области.")

    # Получение всех других магазинов (если редактирование — исключаем текущий ID)
    query = select(Store)
    if store_id:
      query = query.where(Store.id != store_id)
    result = await db.execute(query)
    existing_stores = result.scalars().all()

    # Проверка: полигон не должен пересекаться с другими
    for other_store in existing_stores:
      if other_store.area:
        other_area = load_wkb(bytes(other_store.area.data))
        if area_geom.intersects(other_area):
          return ResponseUtils.error(message="Область нового магазина пересекается с другой.")

  @staticmethod
  async def get_store_by_id(db: AsyncSession, store_id: UUID) -> StoreModel:
    query = (
      select(StoreModel)
      .options(
        selectinload(StoreModel.categories),
      )
      .where(StoreModel.id == store_id)
    )
    result = await db.execute(query)
    store = result.scalar_one_or_none()
    if not store:
      raise NoResultFound(f"Store with ID {store_id} not found")
    return store

  @staticmethod
  async def get_all_stores(db: AsyncSession) -> List[Store]:
    query = (
      select(StoreModel)
      .options(
        selectinload(StoreModel.categories),
      )
    )
    result = await db.execute(query)
    stores = list(result.scalars().all())
    return stores

  @staticmethod
  async def get_stores_by_city(db: AsyncSession, city_id: UUID) -> List[StoreModel]:
    result = await db.execute(
      select(StoreModel)
      .options(
        selectinload(StoreModel.categories)
      )
      .where(StoreModel.city_id == city_id)
    )
    return list(result.scalars().all())

  @staticmethod
  async def create_store(db: AsyncSession, store_data: CreateStore) -> StoreModel:
    point = None
    polygon = None
    if store_data.point:
        x, y = store_data.point
        point = Point(x, y)
    if store_data.area:
        polygon = Polygon(store_data.area)

    if point and polygon:
        await StoreService.validate_geometry(db, to_wkb(point), to_wkb(polygon))

    new_store = StoreModel(
        address=store_data.address,
        start_working_hours=store_data.start_working_hours,
        end_working_hours=store_data.end_working_hours,
        start_delivery_time=store_data.start_delivery_time,
        end_delivery_time=store_data.end_delivery_time,
        phone_number=store_data.phone_number,
        min_order_price=store_data.min_order_price,
        city_id=store_data.city_id,
        created_at=store_data.created_at,
        updated_at=store_data.updated_at
    )

    if polygon:
        new_store.area = from_shape(polygon)
    if point:
        new_store.point = from_shape(point)

    db.add(new_store)
    await db.commit()
    await db.refresh(new_store)

    return new_store

  @staticmethod
  async def update_store(db: AsyncSession, store_data: UpdateStore) -> StoreModel:
    store = await StoreService.get_store_by_id(db, store_data.id)

    point = None
    polygon = None
    if store_data.point:
      x, y = store_data.point
      point = Point(x, y)
    if store_data.area:
      polygon = Polygon(store_data.area)

    if point and polygon:
      await StoreService.validate_geometry(db, to_wkb(point), to_wkb(polygon), store_data.id)

    store.address = store_data.address
    store.start_working_hours = store_data.start_working_hours
    store.end_working_hours = store_data.end_working_hours
    store.start_delivery_time = store_data.start_delivery_time
    store.end_delivery_time = store_data.end_delivery_time
    store.phone_number = store_data.phone_number
    store.min_order_price = store_data.min_order_price
    store.updated_at = datetime.now()

    if polygon:
      store.area = from_shape(polygon)
    if point:
      store.point = from_shape(point)

    await db.commit()
    await db.refresh(store)
    return store

  @staticmethod
  async def delete_store(db: AsyncSession, store_id: UUID) -> None:
    store = await StoreService.get_store_by_id(db, store_id)
    await db.delete(store)
    await db.commit()

  @staticmethod
  async def convert_geometry(store_model):
    if store_model.point:
      point_geom = cast(Point, load_wkb(bytes(store_model.point.data)))
      store_model.point = [point_geom.x, point_geom.y]
    if store_model.area:
      area_geom = cast(Polygon, load_wkb(bytes(store_model.area.data)))
      store_model.area = [list(coord) for coord in area_geom.exterior.coords]
    return store_model