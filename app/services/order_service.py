from decimal import Decimal
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.db.models import (Order, OrderItem, OrderAddress, ProductVariant, Store)
from app.db.models.orders import OrderItemIngredient
from app.schemas.order import (OrderCreate, OrderRead, OrderAddressRead, OrderItemRead, OrderStatusUpdate, OrderItemIngredientRead)

class OrderService:
  async def list_orders_by_user(
      db: AsyncSession,
      user_id: UUID
  ) -> List[OrderRead]:
    stmt = (
      select(Order)
      .where(Order.user_id == user_id)
      .options(
        selectinload(Order.address),
        selectinload(Order.items)
        .selectinload(OrderItem.custom_ingredients)
      )
      .order_by(Order.created_at.desc())
    )
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return [OrderService._to_read(o) for o in orders]

  @staticmethod
  async def list_orders_by_store(
      db: AsyncSession,
      store_id: UUID
  ) -> List[OrderRead]:
    stmt = (
      select(Order)
      .where(Order.store_id == store_id)
      .options(
        selectinload(Order.address),
        selectinload(Order.items)
        .selectinload(OrderItem.custom_ingredients)
      )
      .order_by(Order.created_at.desc())
    )
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return [OrderService._to_read(o) for o in orders]

  @staticmethod
  async def list_orders_by_store_filter_statuses(
      db: AsyncSession,
      store_id: UUID,
      status_values: List[int]
  ) -> List[OrderRead]:
    from app.db.models import OrderStatus

    include, exclude = [], []
    for code in status_values:
      try:
        enum_val = OrderStatus(abs(code))
      except ValueError:
        continue
      (include if code >= 0 else exclude).append(enum_val)

    stmt = (
      select(Order)
      .where(
        or_(
          Order.store_id == store_id,
          Order.is_pickup.is_(False)
        ))
      .options(
        selectinload(Order.address),
        selectinload(Order.items)
        .selectinload(OrderItem.custom_ingredients)
      )
      .order_by(Order.created_at.desc())
    )
    if exclude and not include:
      stmt = stmt.where(~Order.status.in_(exclude))
    elif include:
      stmt = stmt.where(Order.status.in_(include))

    result = await db.execute(stmt)
    orders = result.scalars().all()
    return [OrderService._to_read(o) for o in orders]


  @staticmethod
  async def create_order(
      db: AsyncSession,
      data: OrderCreate,
      user
  ) -> OrderRead:

    if data.is_pickup and not data.store_id:
      raise HTTPException(400, "store_id is required for pickup")
    if not data.is_pickup and not data.address:
      raise HTTPException(400, "address is required for delivery")
    if data.is_pickup:
      store = await db.get(Store, data.store_id)
      if not store:
        raise HTTPException(404, "Store not found")

    order = Order(
      user_id=user.id,
      is_pickup=data.is_pickup,
      store_id=data.store_id,
      payment_method=data.payment_method,
    )
    db.add(order)
    await db.flush()

    if data.address and not data.is_pickup:
      addr = OrderAddress(
        order_id=order.id,
        **data.address.dict()
      )
      db.add(addr)

    total = Decimal(0)

    for item in data.items:
      stmt = (
        select(ProductVariant)
        .where(ProductVariant.id == item.product_variant_id)
        .options(selectinload(ProductVariant.product))
      )
      variant = (await db.execute(stmt)).scalar_one_or_none()
      if not variant:
        raise HTTPException(404, f"Variant {item.product_variant_id} not found")
      price = Decimal(variant.price)
      oi = OrderItem(
        order_id=order.id,
        product_variant_id=variant.id,
        quantity=item.quantity,
        price_per_item=price,
        product_name=variant.product.name,
        variant_size=variant.size,
        type=item.type,
        dough=item.dough,
      )
      db.add(oi)
      await db.flush()

      for ci in item.added_ingredients + item.removed_ingredients:
        db.add(OrderItemIngredient(
          order_item_id=oi.id,
          ingredient_id=ci.ingredient_id,
          quantity=ci.quantity,
          is_removed=ci.is_removed
        ))

      total += oi.price_per_item * oi.quantity

    order.total_price = float(total)
    await db.commit()
    await db.refresh(order)


    stmt = (
      select(Order)
      .where(Order.id == order.id)
      .options(
        selectinload(Order.address),
        selectinload(Order.items).selectinload(OrderItem.custom_ingredients)
      )
    )
    fresh = (await db.execute(stmt)).scalars().one()
    return OrderService._to_read(fresh)

  @staticmethod
  async def update_order_status(
      db: AsyncSession,
      data: OrderStatusUpdate
  ) -> OrderRead:
    order = await db.get(Order, data.id_order)
    if not order:
      raise HTTPException(status_code=404, detail="Order not found")
    order.status = data.status
    await db.commit()
    await db.refresh(order)

    stmt = (
      select(Order)
      .where(Order.id == order.id)
      .options(
        selectinload(Order.address),
        selectinload(Order.items)
        .selectinload(OrderItem.custom_ingredients)
      )
    )
    fresh = (await db.execute(stmt)).scalars().one()
    return OrderService._to_read(fresh)

  @staticmethod
  def _to_read(order: Order) -> OrderRead:

    addr = None
    if order.address:
      addr = OrderAddressRead(**{
        'street': order.address.street,
        'house': order.address.house,
        'apartment': order.address.apartment,
        'comment': order.address.comment,
      })

    items = []
    for oi in order.items:
      added, removed = [], []
      for ci in oi.custom_ingredients:
        ingr = OrderItemIngredientRead(
          ingredient_id=ci.ingredient_id,
          quantity=ci.quantity,
          is_removed=ci.is_removed,
          ingredient_name=ci.ingredient.name,
        )
        (removed if ci.is_removed else added).append(ingr)

      items.append(OrderItemRead(
        product_variant_id=oi.product_variant_id,
        quantity=oi.quantity,
        price_per_item=float(oi.price_per_item),
        product_name=oi.product_name,
        variant_size=oi.variant_size,
        type=oi.type,
        dough=oi.dough,
        added_ingredients=added,
        removed_ingredients=removed,
      ))

    return OrderRead(
      id=order.id,
      user_id=order.user_id,
      total_price=order.total_price,
      is_pickup=order.is_pickup,
      store_id=order.store_id,
      payment_method=order.payment_method,
      status=order.status.value,
      created_at=order.created_at,
      address=addr,
      items=items,
    )
