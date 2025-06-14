from typing import List, Any, Coroutine
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query
from fastapi.params import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityMiddleware
from app.db import get_db
from app.db.models import User, Order
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate, OrderStatus
from app.services.order_service import OrderService
from app.services.response_utils import ResponseUtils

router = APIRouter()
@router.get(
  "/me",
)
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    token: str = Header(None),
):
  user_or_error = await SecurityMiddleware.get_user_or_error_dict(token, db)
  if isinstance(user_or_error, dict):
    return user_or_error
  user: User = user_or_error
  orders = await OrderService.list_orders_by_user(db, user.id)
  return ResponseUtils.success(orders=orders)

@router.get(
  "/store/{store_id}",
)
async def get_store_orders(
  store_id: UUID,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None),
)->dict:
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  return ResponseUtils.success(orders=await OrderService.list_orders_by_store(db, store_id))

@router.get(
    "/store/{store_id}/filter",
)
async def get_store_orders_filtered(
  store_id: UUID,
  statuses: List[int] = Query(
    None,
    alias="status",
    description=(
      "Список значений статусов: "
      "положительные для включения; "
      "отрицательные для исключения (e.g. -1 — исключить статус 1)"
    )
  ),
  db: AsyncSession = Depends(get_db),
  token: str = Header(None),
) -> dict:
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")

  auth = await SecurityMiddleware.is_not_user(token, db)
  if isinstance(auth, dict):
    return auth

  orders = await OrderService.list_orders_by_store_filter_statuses(
    db, store_id, statuses or []
  )
  return ResponseUtils.success(orders=orders)
@router.post("/")
async def place_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Header(None),
)->dict:
  user_or_error = await SecurityMiddleware.get_user_or_error_dict(token, db)
  if isinstance(user_or_error, dict):
    return user_or_error
  user: User = user_or_error
  order = await OrderService.create_order(db, payload,user)
  return ResponseUtils.success(order=order)

@router.put("/update_order_status")
async def update_order_status(
  data: OrderStatusUpdate,
  db: AsyncSession = Depends(get_db),
  token: str = Header(None),
)->dict:
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_not_user(token, db)
  res = await OrderService.update_order_status(db, data)
  if res is not None:
    return ResponseUtils.success(order=res)
  return ResponseUtils.error(message='Ошибка')

