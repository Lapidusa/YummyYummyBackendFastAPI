import json

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile
from fastapi.params import File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Ingredient
from app.services.ingredient_service import IngredientService
from app.schemas.ingredient import IngredientCreate, IngredientUpdate, IngredientOut
from uuid import UUID
from app.db import get_db
from app.services.response_utils import ResponseUtils
from app.core.security import SecurityMiddleware

router = APIRouter()

@router.get("/", response_model=list[IngredientOut] )
async def get_ingredients(db: AsyncSession = Depends(get_db)):
  return await IngredientService.get_all(db)

@router.get("/{ingredient_id}", response_model=IngredientOut)
async def get_ingredient(ingredient_id: UUID, db: AsyncSession = Depends(get_db)):
  ingredient = await IngredientService.get_by_id(ingredient_id, db)
  if not ingredient:
    raise HTTPException(status_code=404, detail="Ингредиент не найден")
  return ingredient

@router.post("/", response_model=IngredientOut)
async def create_ingredient(ingredient_data_json: str = Form(...), image: UploadFile | None = File(None), db: AsyncSession = Depends(get_db), token: str = Header(None)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  data = json.loads(ingredient_data_json)
  name = data.get("name")
  image_path = None

  if image:
    file_location = f"media/ingredients/{image.filename}"
    with open(file_location, "wb") as f:
      f.write(await image.read())
    image_path = file_location
  ingredient = Ingredient(name=name, image=image_path)
  return await IngredientService.create(ingredient, db)

@router.put("/{ingredient_id}", response_model=IngredientOut)
async def update_ingredient(ingredient_id: UUID, ingredient_data_json: str = Form(...), image: UploadFile | None = File(None), db: AsyncSession = Depends(get_db), token: str = Header(None)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)

  data = json.loads(ingredient_data_json)
  name = data.get("name")
  image_path = None

  if image:
    file_location = f"media/ingredients/{image.filename}"
    with open(file_location, "wb") as f:
      f.write(await image.read())
    image_path = file_location
  ingredient = Ingredient(name=name, image=image_path)
  ingredient = await IngredientService.update(ingredient_id, ingredient, db)
  if not ingredient:
    ResponseUtils.error(message="Ингредиент не найден или удалён")
  return ingredient

@router.delete("/{ingredient_id}")
async def delete_ingredient(ingredient_id: UUID, db: AsyncSession = Depends(get_db), token: str = Header(None)):
  if token is None:
    return ResponseUtils.error(message="Токен не предоставлен")
  await SecurityMiddleware.is_admin_or_manager(token, db)
  ingredient = await IngredientService.delete(ingredient_id, db)
  if not ingredient:
    ResponseUtils.error(message="Ингредиент не найден")
  return {"message": "Ингредиент удалён"}
