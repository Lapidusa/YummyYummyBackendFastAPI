from typing import Union, Any, Coroutine, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_polymorphic

from app.db.models import CartItem as CartItemModel, PizzaCartItem as PizzaCartItemModel, CartItemIngredient,\
  PizzaCartItem, CartItem, ProductVariant, Ingredient
from app.db.models import User

from app.schemas.cart_item import (
  CartItemCreate,
  SimpleCartItem as SimpleCartItemSchema,
  PizzaCartItem as PizzaCartItemSchema, AddedIngredient, CartItemIngredientOut, PizzaCartItemOut, SimpleCartItem,
  SimpleCartItemOut, RemovedIngredient,
)
from app.schemas.product import ProductVariantOut


class CartItemService:
  @staticmethod
  async def get_user_cart(
      db: AsyncSession,
      user: User
  ) -> list[Union[SimpleCartItemOut, PizzaCartItemOut]]:
    pizza_union = with_polymorphic(CartItem, [PizzaCartItem])
    stmt = (
      select(pizza_union)
      .where(pizza_union.user_id == user.id)
      .options(
        selectinload(pizza_union.product_variant)
        .selectinload(ProductVariant.product),
        selectinload(pizza_union.PizzaCartItem.custom_ingredients)
        .selectinload(CartItemIngredient.ingredient)
      )
    )
    items = (await db.execute(stmt)).scalars().all()

    result: list[Union[SimpleCartItemOut, PizzaCartItemOut]] = []
    for item in items:
      variant_out = ProductVariantOut.model_validate(item.product_variant)
      product_name = item.product_variant.product.name
      if isinstance(item, PizzaCartItem):
        added, removed = [], []
        for ing in item.custom_ingredients:
          entry = CartItemIngredientOut.model_validate({
            "ingredient": ing.ingredient,
            "quantity": ing.quantity,
          })
          if ing.is_removed:
            removed.append(entry)
          else:
            added.append(entry)

        result.append(PizzaCartItemOut.model_validate({
          "id": item.id,
          "quantity": item.quantity,
          "dough": item.dough,
          "price": item.price,
          "type": 'pizza',
          "name": product_name,
          "added_ingredients": added,
          "removed_ingredients": removed,
          "variant": item.product_variant
        }))
      else:
        result.append(SimpleCartItemOut.model_validate({
          "id": item.id,
          "quantity": item.quantity,
          "price": item.price,
          "name": product_name,
          "type": "simple",
          "variant": item.product_variant
        }))

    return result

  @staticmethod
  async def add_or_update_item(
      data: CartItemCreate,
      db: AsyncSession,
      user: User
  ) -> Optional[Union[CartItemModel, PizzaCartItemModel]]:

    if data.type == "simple":
      simple: SimpleCartItemSchema = data

      stmt_simple = select(CartItemModel).where(
        CartItemModel.user_id == user.id,
        CartItemModel.product_variant_id == simple.product_variant_id,
      )
      existing_simple = (await db.execute(stmt_simple)).scalars().first()

      if existing_simple:
        new_qty = existing_simple.quantity + simple.quantity
        if new_qty <= 0:
          await db.delete(existing_simple)
          await db.commit()
          db.expunge(existing_simple)
          return None

        existing_simple.quantity = new_qty
        await db.commit()
        await db.refresh(existing_simple)
        return existing_simple

      return await CartItemService.add_simple_item(simple, db, user)

    elif data.type == "pizza":
      pizza_data: PizzaCartItemSchema = data
      stmt_pizza = (
        select(PizzaCartItemModel)
        .where(
          PizzaCartItemModel.user_id == user.id,
          PizzaCartItemModel.product_variant_id == pizza_data.product_variant_id,
          PizzaCartItemModel.dough == pizza_data.dough,
        )
        .options(selectinload(PizzaCartItemModel.custom_ingredients))
      )
      existing_pizza = (await db.execute(stmt_pizza)).scalars().first()

      if existing_pizza and CartItemService.ingredients_match(
          existing_pizza,
          pizza_data.added_ingredients,
          pizza_data.removed_ingredients
      ):
        new_qty = existing_pizza.quantity + pizza_data.quantity
        if new_qty <= 0:
          await db.delete(existing_pizza)
          await db.commit()
          db.expunge(existing_pizza)
          return None

        existing_pizza.quantity = new_qty
        await db.commit()
        await db.refresh(existing_pizza)
        return existing_pizza

      return await CartItemService.add_pizza_item(pizza_data, db, user)
    else:
      raise ValueError("Unknown cart item type")

  @staticmethod
  async def add_simple_item(
      data: SimpleCartItemSchema,
      db: AsyncSession,
      user: User
  ) -> CartItemModel:
    item = CartItemModel(
      user_id=user.id,
      product_variant_id=data.product_variant_id,
      quantity=data.quantity,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

  @staticmethod
  async def add_pizza_item(
      data: PizzaCartItemSchema,
      db: AsyncSession,
      user: User
  ) -> PizzaCartItemModel:
    variant_stmt = select(ProductVariant).where(ProductVariant.id == data.product_variant_id)
    variant = (await db.execute(variant_stmt)).scalars().first()
    base_price = variant.price if variant else 0

    pizza = PizzaCartItem(
      user_id=user.id,
      product_variant_id=data.product_variant_id,
      quantity=data.quantity,
      dough=data.dough
    )
    db.add(pizza)
    await db.flush()
    total_price = base_price
    removed_ids = {ri.ingredient_id for ri in data.removed_ingredients}
    added_ids = {ai.ingredient_id for ai in data.added_ingredients}

    filtered_added = [
      ai
      for ai in data.added_ingredients
      if ai.ingredient_id not in removed_ids
    ]
    filtered_removed_ids = [
      rid
      for rid in removed_ids
      if rid not in added_ids
    ]

    for ai in filtered_added:
      ing = (await db.execute(
        select(Ingredient).where(Ingredient.id == ai.ingredient_id)
      )).scalars().first()
      price = ing.price if ing else 0
      total_price += price * ai.quantity
      db.add(CartItemIngredient(
        cart_item_id=pizza.id,
        ingredient_id=ai.ingredient_id,
        quantity=ai.quantity,
        is_removed=False,
      ))

    for ing_id in filtered_removed_ids:
      db.add(CartItemIngredient(
        cart_item_id=pizza.id,
        ingredient_id=ing_id,
        quantity=0,
        is_removed=True,
      ))

    pizza.price = total_price
    await db.commit()
    await db.refresh(pizza)
    return pizza

  @staticmethod
  def ingredients_match(
      existing: PizzaCartItemModel,
      added: list[AddedIngredient],
      removed: list[RemovedIngredient]
  ) -> bool:
    existing_removed = {i.ingredient_id for i in existing.custom_ingredients if i.is_removed}
    existing_added = {(i.ingredient_id, i.quantity) for i in existing.custom_ingredients if not i.is_removed}

    incoming_removed = {ri.ingredient_id for ri in removed}
    incoming_added = {(i.ingredient_id, i.quantity) for i in added}

    return existing_removed == incoming_removed and existing_added == incoming_added

  @staticmethod
  async def calculate_pizza_price(
      db: AsyncSession,
      product_variant_id: UUID,
      added_ingredients: list[AddedIngredient],
      removed_ingredients: list[RemovedIngredient]
  ) -> int:
    stmt = select(ProductVariant).where(ProductVariant.id == product_variant_id)
    variant = (await db.execute(stmt)).scalars().first()
    base_price = variant.price if variant else 0

    removed_set = {ri.ingredient_id for ri in removed_ingredients}
    filtered_added = [ai for ai in added_ingredients if ai.ingredient_id not in removed_set]

    ingredient_ids = [ai.ingredient_id for ai in filtered_added]
    if not ingredient_ids:
      return base_price

    stmt_ing = select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
    ingredients = {ing.id: ing.price for ing in (await db.execute(stmt_ing)).scalars().all()}

    for ai in filtered_added:
      ing_price = ingredients.get(ai.ingredient_id, 0)
      base_price += ing_price * ai.quantity

    return base_price