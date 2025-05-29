import os
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Product, Category, Ingredient
from app.db.models.products import Type, Pizza, Dough, ProductVariant, PizzaIngredient
from app.schemas.product import ProductCreate, PizzaCreate, ProductUpdate, PizzaUpdate
from typing import Union, cast

ProductUnionCreate = Union[ProductCreate, PizzaCreate]
ProductUnionUpdate = Union[ProductUpdate, PizzaUpdate]
class ProductService:

  @staticmethod
  async def get_products_by_category(db: AsyncSession, category_id: UUID):
    result = await db.execute(
      select(Product)
      .options(selectinload(Product.variants))
      .where(Product.category_id == category_id)
    )
    return result.scalars().all()

  @staticmethod
  async def get_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
      select(Product)
      .options(selectinload(Product.variants))
      .where(Product.id == product_id)
    )
    return result.scalar_one_or_none()

  @staticmethod
  async def get_products_by_store(db: AsyncSession, store_id: UUID):
    result = await db.execute(
      select(Product).join(Category)
      .options(selectinload(Product.variants))
      .where(Product.store_id == store_id)
    )
    return result.scalars().all()

  @staticmethod
  async def create_product(db: AsyncSession, product_data: ProductUnionCreate) -> Product:
    max_position_query = select(func.max(Product.position)).where(
      Product.category_id==product_data.category_id
    )
    result = await db.execute(max_position_query)
    max_position = result.scalar() or 0
    if product_data.type == Type.PIZZA:
      obj = Pizza(
        category_id=product_data.category_id,
        name=product_data.name,
        description=product_data.description,
        position=max_position + 1,
        is_available=product_data.is_available,
        dough=Dough.THICK_DOUGH
      )
      db.add(obj)
      await db.flush()

      ingredient_ids = [i.ingredient_id for i in product_data.ingredients]
      ingredients_result = await db.execute(
        select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
      )
      ingredients_map = {i.id: i for i in ingredients_result.scalars()}

      obj.pizza_ingredients = [
        PizzaIngredient(
          pizza=obj,
          ingredient=ingredients_map[i.ingredient_id],
          is_deleted=i.is_deleted
        )
        for i in product_data.ingredients if i.ingredient_id in ingredients_map
      ]

    else:
      obj = Product(
        category_id=product_data.category_id,
        name = product_data.name,
        description = product_data.description,
        position = max_position + 1,
        is_available = product_data.is_available
      )
    variants = cast(list[ProductVariant], obj.variants)

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
      variants.append(variant)

    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    return obj

  @staticmethod
  async def update_product(db: AsyncSession, product_id: UUID, product_data: ProductUnionUpdate) -> Product:
    product = await ProductService.get_product_by_id(db, product_id)
    product.name = product_data.name
    product.description = product_data.description
    product.is_available = product_data.is_available
    product.category_id = product_data.category_id

    if isinstance(product, Pizza) and isinstance(product_data, PizzaUpdate):
      product.dough = product_data.THICK_DOUGH
      product.pizza_ingredients.clear()

      ingredient_ids = [i.ingredient_id for i in product_data.ingredients]
      ingredients_result = await db.execute(
        select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
      )
      ingredients_map = {i.id: i for i in ingredients_result.scalars()}

      product.pizza_ingredients = [
        PizzaIngredient(
          pizza=product,
          ingredient=ingredients_map[i.ingredient_id],
          is_deleted=i.is_deleted
        )
        for i in product_data.ingredients if i.ingredient_id in ingredients_map
      ]
    variants = cast(list[ProductVariant], product.variants)
    variants.clear()

    for variant_data in product_data.variants:
      variant = ProductVariant(
        size=variant_data.size,
        price=variant_data.price,
        weight=variant_data.weight,
        calories=variant_data.calories,
        proteins=variant_data.proteins,
        fats=variant_data.fats,
        carbohydrates=variant_data.carbohydrates,
        is_available=variant_data.is_available,
        image=variant_data.image
      )
      variants.append(variant)

    await db.commit()
    await db.refresh(product)
    return product

  @staticmethod
  async def delete_product(db: AsyncSession, product_id: UUID) -> bool:
    product = await ProductService.get_product_by_id(db, product_id)

    if not product:
        raise ValueError("Продукт не найден")

    # Удаляем связанные изображения
    for variant in product.variants:
        if variant.image:
            image_path = variant.image.lstrip("/")
            if os.path.exists(image_path):
                os.remove(image_path)

    await db.delete(product)
    await db.commit()
    return True