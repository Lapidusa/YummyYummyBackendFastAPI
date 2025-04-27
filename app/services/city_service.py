from typing import List, cast
from uuid import UUID

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from shapely.wkb import loads as load_wkb
from app.db.models.cities import City as CityModel, City
from app.schemas.city import CreateCity, UpdateCity
from app.services.response_utils import ResponseUtils
import httpx

db: AsyncSession
class CityService:
  @staticmethod
  async def get_city_coordinates(city_name: str) -> dict:
    # Строим запрос к Nominatim API
    async with httpx.AsyncClient() as client:
      response = await client.get(f"https://nominatim.openstreetmap.org/search", params={
        "q": city_name,
        "format": "json",
        "addressdetails": 1,
        "limit": 1,
      })

      if response.status_code != 200:
        raise Exception(f"Ошибка при получении координат для города {city_name}")

      data = response.json()
      if not data:
        raise Exception(f"Город {city_name} не найден")

      # Получаем координаты из ответа
      lat = float(data[0]["lat"])
      lon = float(data[0]["lon"])
      return {"lat": lat, "lon": lon}

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
    point = None
    try:
      coordinates = await CityService.get_city_coordinates(city_data.name)
      if coordinates:
        x, y = coordinates["lon"], coordinates["lat"]
        point = Point(x, y)
    except Exception as e:
      raise Exception(f"Не удалось получить координаты для города {city_data.name}: {str(e)}")

    new_city = CityModel(
      name=city_data.name,
    )
    new_city.point = from_shape(point)

    db.add(new_city)
    await db.commit()
    await db.refresh(new_city)

    return new_city

  @staticmethod
  async def update_city(db: AsyncSession, city_data: UpdateCity) -> City:
    city = await CityService.get_city_by_id(db, city_data.id)
    point = None
    if city.point:
      x, y = city.point
      point = Point(x, y)
    if not city:
      raise ResponseUtils.error(message="Category with ID {category_data.id} not found")
    city.name = city_data.name
    city.point = from_shape(point)
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

  @staticmethod
  async def convert_geometry(city_model):
    if city_model.point:
      point_geom = cast(Point, load_wkb(bytes(city_model.point.data)))
      city_model.point = [point_geom.x, point_geom.y]
    return city_model