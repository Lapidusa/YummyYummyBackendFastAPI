import os
from uuid import UUID
import json
from fastapi import Form, File, Depends, UploadFile, APIRouter, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityMiddleware
from app.db import get_db
from app.schemas.product import ProductCreate, ProductUpdate, PizzaUpdate, TypeProduct, PizzaCreate
from app.services.product_service import ProductService
from app.services.response_utils import ResponseUtils

router = APIRouter()
@router.get("/by-category/{category_id}")
async def get_products_by_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    products = await ProductService.get_products_by_category(db, category_id)
    return ResponseUtils.success(products=products)

@router.get("/{product_id}")
async def get_product_by_id(product_id: UUID, db: AsyncSession = Depends(get_db)):
    product = await ProductService.get_product_by_id(db, product_id)
    if product:
        return ResponseUtils.success(product=product)
    return ResponseUtils.error(message="Продукт не найден")

@router.get("/by-store/{store_id}")
async def get_products_by_store(store_id: UUID, db: AsyncSession = Depends(get_db)):
    products = await ProductService.get_products_by_store(db, store_id)
    return ResponseUtils.success(products=products)

@router.post("/create")
async def create_product(
    product_data_json: str = Form(...),
    images: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    token: str = Header(None)
):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  try:
    parsed_data = json.loads(product_data_json)
    variants_data = parsed_data.get("variants", [])
  except json.JSONDecodeError:
    return ResponseUtils.error("Некорректный формат JSON данных")

  try:
    if len(images) != len(variants_data):
      return ResponseUtils.error("Количество изображений должно соответствовать количеству вариантов")

    for i, image in enumerate(images):
      if not image.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        return ResponseUtils.error(f"Недопустимый формат изображения: {image.filename}")

      save_path = f"media/products/{image.filename}"
      os.makedirs(os.path.dirname(save_path), exist_ok=True)

      with open(save_path, "wb") as f:
        f.write(await image.read())

      variants_data[i]["image"] = f"/media/products/{image.filename}"

    parsed_data["variants"] = variants_data
    product_type = parsed_data.get("type")

    if product_type == TypeProduct.PIZZA:
      product_data = PizzaCreate(**parsed_data)
    else:
      product_data = ProductCreate(**parsed_data)

  except Exception as e:
    return ResponseUtils.error(f"Ошибка валидации: {str(e)}")

  product = await ProductService.create_product(db, product_data)
  return ResponseUtils.success(product=product)

@router.put("/update/{product_id}")
async def update_product(
    product_id: UUID,
    product_data_json: str = Form(...),
    images: list[UploadFile] = File(default_factory=list),
    db: AsyncSession = Depends(get_db),
    token: str = Header(None)
):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  try:
    parsed_data = json.loads(product_data_json)
    variants_data = parsed_data.get("variants", [])
  except json.JSONDecodeError:
    return ResponseUtils.error("Некорректный формат JSON данных")

  image_index = 0
  for i, variant in enumerate(variants_data):
    # если изображение поменялось — берём из images
    if variant.get("changed_image"):
      if image_index >= len(images):
        return ResponseUtils.error(f"Нет изображения для варианта {i + 1}")

      image = images[image_index]

      if not image.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        return ResponseUtils.error(f"Недопустимый формат изображения: {image.filename}")

      save_path = f"media/products/{image.filename}"
      os.makedirs(os.path.dirname(save_path), exist_ok=True)

      with open(save_path, "wb") as f:
        f.write(await image.read())

      variant["image"] = f"/media/products/{image.filename}"
      image_index += 1

    # если не поменялось, но image всё равно строка — оставляем как есть
    elif isinstance(variant.get("image"), str):
      if not variant["image"].startswith("/media/products/"):
        variant["image"] = f"/media/products/{variant['image']}"

    else:
      return ResponseUtils.error(f"Для варианта {i + 1} не указано изображение")

  print("Final variants data to be passed into schema:", variants_data)
  parsed_data["variants"] = variants_data

  try:
    product_data = ProductUpdate(**parsed_data)
  except Exception as e:
    try:
      product_data = PizzaUpdate(**parsed_data)
    except Exception as e:
      return ResponseUtils.error(f"Ошибка валидации: {str(e)}")

  try:
    product = await ProductService.update_product(db, product_id, product_data)
  except ValueError as e:
    return ResponseUtils.error(str(e))

  return ResponseUtils.success(product=product)

@router.delete("/delete/{product_id}")
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    token: str = Header(None)
):
    if token is None:
        return ResponseUtils.error(message="Токен не предоставлен")
    await SecurityMiddleware.is_admin_or_manager(token, db)

    try:
        await ProductService.delete_product(db, product_id)
        return ResponseUtils.success(message="Продукт удалён")
    except ValueError as e:
        return ResponseUtils.error(str(e))