from fastapi import APIRouter, Depends
from fastapi.params import Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import SecurityMiddleware
from app.db import get_db
from app.db.models import User
from app.schemas.cart_item import CartItemCreate
from app.services.cart_item_service import CartItemService
from app.services.response_utils import ResponseUtils

router = APIRouter()
@router.get("/cart/", response_model=None)
async def get_user_cart(
    db: AsyncSession = Depends(get_db),
    token: str = Header(..., alias="token")
):
    user_or_error = await SecurityMiddleware.get_user_or_error_dict(token, db)
    if isinstance(user_or_error, dict):
        return user_or_error
    user: User = user_or_error

    result = await CartItemService.get_user_cart(db, user)
    return ResponseUtils.success(cart=result)
@router.post("/preview-price", response_model=None)
async def get_preview_price(
    data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
):
    if data.type == 'simple':
        price = data.variant.price
    else:
        price = await CartItemService.calculate_pizza_price(
            db,
            data.product_variant_id,
            data.added_ingredients,
            data.removed_ingredients
        )
    return ResponseUtils.success(price=price)
@router.post("/add-to-cart-item/", response_model=None)
async def add_to_cart_item(
    data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Header(..., alias="token")
):
    user_or_error = await SecurityMiddleware.get_user_or_error_dict(token, db)
    if isinstance(user_or_error, dict):
        return user_or_error
    user: User = user_or_error

    result = await CartItemService.add_or_update_item(data, db, user)
    if result is None:
        return ResponseUtils.success(message="Успешно удален")
    return ResponseUtils.success(cart_item=result)
