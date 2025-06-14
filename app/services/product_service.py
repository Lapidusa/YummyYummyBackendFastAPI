import os
from uuid import UUID

from fastapi import HTTPException
from pydantic import Field
from sqlalchemy import select, func, delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Product, Category, Ingredient
from app.db.models.products import Type, Pizza, ProductVariant, PizzaIngredient, Dough
from app.schemas.product import ProductCreate, PizzaCreate, ProductUpdate, PizzaUpdate, ProductResponse
from typing import Union, cast, Annotated

ProductUnionCreate = Union[ProductCreate, PizzaCreate]
ProductUnionUpdate = Annotated[
  Union[PizzaUpdate, ProductUpdate],
  Field(discriminator="type")
]
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
  async def create_product(db: AsyncSession, product_data: ProductUnionCreate) -> dict:
    max_position_query = select(func.max(Product.position)).where(
      Product.category_id == product_data.category_id
    )
    result = await db.execute(max_position_query)
    max_position = result.scalar() or 0

    if product_data.type == Type.PIZZA:
      assert isinstance(product_data, PizzaCreate)
      obj = Pizza(
        category_id=product_data.category_id,
        name=product_data.name,
        description=product_data.description,
        position=max_position + 1,
        is_available=product_data.is_available,
        dough=Dough.THICK_DOUGH,
        type=Type.PIZZA,
      )
      db.add(obj)
      await db.flush()

      ingredient_ids = [i.ingredient_id for i in product_data.ingredients]
      pizza_ingredients = [
        PizzaIngredient(
          pizza_id=obj.id,
          ingredient_id=i.ingredient_id,
          is_deleted=i.is_deleted,
        )
        for i in product_data.ingredients
      ]
      db.add_all(pizza_ingredients)
    else:
      obj = Product(
        category_id=product_data.category_id,
        name=product_data.name,
        description=product_data.description,
        position=max_position + 1,
        is_available=product_data.is_available,
        type=Type.GROUP,
      )
      db.add(obj)
      await db.flush()

    for variant_data in product_data.variants:
      variant = ProductVariant(
        product_id=obj.id,
        size=variant_data.size,
        price=variant_data.price,
        weight=variant_data.weight,
        calories=variant_data.calories,
        proteins=variant_data.proteins,
        fats=variant_data.fats,
        carbohydrates=variant_data.carbohydrates,
        is_available=variant_data.is_available,
        image=variant_data.image,
      )
      db.add(variant)
      await db.refresh(obj, attribute_names=["variants"])

      obj.variants = cast(list[ProductVariant], obj.variants)

    await db.commit()

    if product_data.type == Type.PIZZA:
      stmt = (
        select(Pizza)
        .where(Product.id == obj.id)
        .options(
          selectinload(Pizza.variants),
          selectinload(Pizza.pizza_ingredients).selectinload(PizzaIngredient.ingredient),
        )
      )
    else:
      stmt = (
        select(Product)
        .where(Product.id == obj.id)
        .options(
          selectinload(Product.variants),
        )
      )
    result = await db.execute(stmt)
    full_obj = result.scalar_one()
    try:
      return ProductResponse.model_validate(full_obj).model_dump()
    except Exception as e:
      raise e

  @staticmethod
  async def update_product(
      db: AsyncSession,
      product_id: UUID,
      product_data: ProductUnionUpdate
  ) -> Product:
    stmt = select(Product).where(Product.id == product_id)
    product = (await db.execute(stmt)).scalar_one_or_none()
    if product is None:
      raise HTTPException(404, "Продукт не найден")

    product.name = product_data.name
    product.description = product_data.description
    product.is_available = product_data.is_available
    product.category_id = product_data.category_id
    product.type = product_data.type
    await db.flush()

    if isinstance(product_data, PizzaUpdate):
      existing = await db.execute(
        select(Pizza.id).where(Pizza.id == product_id)
      )
      if existing.scalar_one_or_none() is None:
        await db.execute(
          insert(Pizza.__table__)
          .values(id=product_id, dough=product_data.dough)
        )
        await db.flush()
      else:
        await db.execute(
          update(Pizza.__table__)
          .where(Pizza.__table__.c.id == product_id)
          .values(dough=product_data.dough)
        )
        await db.flush()

      await db.execute(
        delete(PizzaIngredient)
        .where(PizzaIngredient.pizza_id == product_id)
      )
      await db.flush()

      ids = [ing.ingredient_id for ing in product_data.ingredients]
      res = await db.execute(
        select(Ingredient).where(Ingredient.id.in_(ids))
      )
      ingr_map = {i.id: i for i in res.scalars()}

      new_assocs = [
        PizzaIngredient(
          pizza_id=product_id,
          ingredient_id=ing.ingredient_id,
          is_deleted=ing.is_deleted
        )
        for ing in product_data.ingredients
        if ing.ingredient_id in ingr_map
      ]
      db.add_all(new_assocs)
      await db.flush()

    else:
      await db.execute(
        delete(PizzaIngredient)
        .where(PizzaIngredient.pizza_id == product_id)
      )
      await db.execute(
        delete(Pizza).where(Pizza.id == product_id)
      )
      await db.flush()

    await db.execute(
      delete(ProductVariant)
      .where(ProductVariant.product_id == product_id)
    )
    await db.flush()

    for v in product_data.variants:
      db.add(ProductVariant(
        product_id=product_id,
        size=v.size,
        price=v.price,
        weight=v.weight,
        calories=v.calories,
        proteins=v.proteins,
        fats=v.fats,
        carbohydrates=v.carbohydrates,
        is_available=v.is_available,
        image=v.image,
      ))
    await db.flush()

    await db.commit()
    await db.refresh(product)
    return product

  @staticmethod
  async def delete_product(db: AsyncSession, product_id: UUID) -> bool:
    product = await ProductService.get_product_by_id(db, product_id)

    if not product:
      return False

    for variant in product.variants:
      if variant.image:
        image_path = variant.image.lstrip("/")
        if os.path.exists(image_path):
          os.remove(image_path)

    await db.delete(product)
    await db.commit()
    return True