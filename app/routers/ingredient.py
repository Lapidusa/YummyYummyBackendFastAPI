import json
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile
from fastapi.params import File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Ingredient
from app.services.ingredient_service import IngredientService
from uuid import UUID
from app.db import get_db
from app.services.response_utils import ResponseUtils
from app.core.security import SecurityMiddleware

router = APIRouter()

@router.get("/")
async def get_ingredients(db: AsyncSession = Depends(get_db)):
  return ResponseUtils.success(ingredients = await IngredientService.get_all(db))

@router.get("/{ingredient_id}")
async def get_ingredient(ingredient_id: UUID, db: AsyncSession = Depends(get_db)):
  ingredient = await IngredientService.get_by_id(ingredient_id, db)
  if not ingredient:
    raise HTTPException(status_code=404, detail="Ингредиент не найден")
  return ResponseUtils.success(ingredients = ingredient)

@router.post("/")
async def create_ingredient(ingredient_data_json: str = Form(...), images: Optional[List[UploadFile]] | None = File(None), db: AsyncSession = Depends(get_db), token: str = Header(None)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  data = json.loads(ingredient_data_json)
  name = data.get("name")
  price = data.get("price")

  image_path: Optional[str] = None
  overlay_path: Optional[str] = None

  if images:
    os.makedirs("media/ingredients", exist_ok=True)
    os.makedirs("media/ingredients/overlays", exist_ok=True)
    if len(images) >= 1:
      main_file = images[0]
      main_location = os.path.join("media", "ingredients", main_file.filename)
      with open(main_location, "wb") as f:
        f.write(await main_file.read())
      image_path = f"/{main_location.replace(os.sep, '/')}"

    if len(images) >= 2:
      overlay_file = images[1]
      overlay_location = os.path.join("media", "ingredients", "overlays", overlay_file.filename)
      with open(overlay_location, "wb") as f:
        f.write(await overlay_file.read())
      overlay_path = f"/{overlay_location.replace(os.sep, '/')}"
  ingredient_dict = {
    "name": name,
    "image": image_path,
    "overlay_image": overlay_path,
    "price": price,
  }
  return ResponseUtils.success(ingredients = await IngredientService.create(ingredient_dict, db))

@router.put("/{ingredient_id}")
async def update_ingredient(ingredient_id: UUID, ingredient_data_json: str = Form(...), images: Optional[List[UploadFile]] = File(None), db: AsyncSession = Depends(get_db), token: str = Header(None)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)
  try:
    data = json.loads(ingredient_data_json)
  except json.JSONDecodeError:
    return ResponseUtils.error("Некорректный формат JSON данных")

  name = data.get("name")
  price = data.get("price")

  result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
  existing: Ingredient | None = result.scalar_one_or_none()
  if not existing:
    return ResponseUtils.error(message="Ингредиент не найден")

  update_data: dict = {}
  if name is not None:
    update_data["name"] = name
  if price is not None:
    update_data["price"] = price

  if images:
    if len(images) >= 1:
      main_file = images[0]
      if not main_file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        return ResponseUtils.error(f"Недопустимый формат файла: {main_file.filename}")

      os.makedirs("media/ingredients", exist_ok=True)
      fname = main_file.filename
      save_path = os.path.join("media", "ingredients", fname)
      with open(save_path, "wb") as f:
        f.write(await main_file.read())

      update_data["image"] = f"/media/ingredients/{fname}"

    if len(images) >= 2:
      overlay_file = images[1]
      if not overlay_file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        return ResponseUtils.error(f"Недопустимый формат файла: {overlay_file.filename}")

      os.makedirs("media/ingredients/overlays", exist_ok=True)
      fname2 = overlay_file.filename
      save_path2 = os.path.join("media", "ingredients", "overlays", fname2)
      with open(save_path2, "wb") as f:
        f.write(await overlay_file.read())

      update_data["overlay_image"] = f"/media/ingredients/overlays/{fname2}"
  if not update_data:
    return ResponseUtils.success(ingredient=existing)
  updated = await IngredientService.update(ingredient_id, update_data, db)
  return ResponseUtils.success(ingredient=updated)

@router.delete("/{ingredient_id}")
async def delete_ingredient(ingredient_id: UUID, db: AsyncSession = Depends(get_db), token: str = Header(None)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  ingredient = await IngredientService.delete(ingredient_id, db)
  if not ingredient:
    ResponseUtils.error(message="Ингредиент не найден")
  return ResponseUtils.success( message = "Ингредиент удалён")
