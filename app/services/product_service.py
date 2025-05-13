from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product, Category
from app.db.models.products import Type, Pizza, Dough, ProductVariant
from app.schemas.product import ProductCreate

class ProductService:
  @staticmethod
  async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
    max_position_query = select(func.max(Product.position)).where(
      Product.category_id == product_data.category_id
    )
    result = await db.execute(max_position_query)
    max_position = result.scalar() or 0
    if product_data.type == Type.PIZZA:
      if product_data.dough is None:
        raise ValueError("Для пиццы нужно указать тип теста")
      obj = Pizza(
        name = product_data.name,
        description = product_data.description,
        position = max_position + 1,
        is_available = product_data.is_available,
        dough = Dough[product_data.dough.upper()]
      )
    else:
      obj = Product(
        name = product_data.name,
        description = product_data.description,
        position = max_position + 1,
        is_available = product_data.is_available
      )

    # Добавляем варианты
    for variant_data in product_data.variants:
      variant = ProductVariant(
        size = variant_data.size,
        price = variant_data.price,
        weight = variant_data.weight,
        calories = variant_data.calories,
        proteins = variant_data.proteins,
        fats = variant_data.fats,
        carbohydrates = variant_data.carbohydrates,
        is_available = variant_data.is_available,
        image = variant_data.image
      )
      obj.variants.append(variant)

    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    return obj

  @staticmethod
  async def get_products_by_category(db: AsyncSession, category_id: UUID):
    result = await db.execute(
      select(Product).where(Product.category_id == category_id)
    )
    return result.scalars().all()

  @staticmethod
  async def get_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
      select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()

  @staticmethod
  async def get_products_by_store(db: AsyncSession, store_id: UUID):
    result = await db.execute(
      select(Product).join(Category).where(Category.store_id == store_id)
    )
    return result.scalars().all()