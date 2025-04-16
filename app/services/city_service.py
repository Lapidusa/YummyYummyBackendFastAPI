from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.cities import City as CityModel, City
from app.schemas.city import CreateCity, UpdateCity
from app.services.response_utils import ResponseUtils

db: AsyncSession
class CityService:
  @staticmethod
  async def get_city_by_id(db: AsyncSession, city_id: UUID) -> CityModel:
    query = select(CityModel).where(CityModel.id == city_id)
    result = await db.execute(query)
    city =  result.scalar_one_or_none()
    if not city:
      raise NoResultFound(f"City with id {city_id} not found")
    return city

  @staticmethod
  async def get_all_cities(db: AsyncSession) -> List[City]:
    query = select(CityModel)
    result = await db.execute(query)
    cities = list(result.scalars().all())
    return cities

  @staticmethod
  async def create_city(db: AsyncSession, city_data: CreateCity) -> City:
    new_city = CityModel(
      name=city_data.name,
    )
    db.add(new_city)
    await db.commit()
    await db.refresh(new_city)
    return new_city

  @staticmethod
  async def update_city(db: AsyncSession, city_data: UpdateCity) -> City:
    city = await CityService.get_city_by_id(db, city_data.id)
    if not city:
      raise ResponseUtils.error(message="Category with ID {category_data.id} not found")
    city.name = city_data.name
    city.store_id = city_data.store_id
    city.is_available = city_data.is_available
    city.type = city_data.type
    await db.commit()
    await db.refresh(city)
    return city

  @staticmethod
  async def delete_city(db: AsyncSession, city_id: UUID) -> None:
    city = await CityService.get_city_by_id(db, city_id)
    if not city:
      raise ResponseUtils.error(message="Category with ID {city_id} not found")
    await db.delete(city)
    await db.commit()
