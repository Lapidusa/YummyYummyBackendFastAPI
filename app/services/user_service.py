import uuid
from typing import Type, List, Union, Any, Dict

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.core.security import SecurityMiddleware
from app.db.models.users import User, Roles
from app.routers.user import UserPayload
from app.schemas.user import UpdateUserForm
from app.services.response_utils import ResponseUtils

class UserService:
  @staticmethod
  async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User or None:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
      return None

    return user

  @staticmethod
  async def create_new_user(db: AsyncSession, phone_number: str) -> User:
    new_user = User(
      id = uuid.uuid4(),
      phone_number = phone_number,
      role = Roles.USER,
      created_at = datetime.now(timezone.utc),
      scores = 0
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

  @staticmethod
  async def create_for_admin(db: AsyncSession, user_data: UserPayload) -> User:
    new_user = User(
      id = uuid.uuid4(),
      phone_number = user_data.phone_number,
      role = user_data.role,
      name = user_data.name,
      created_at = datetime.now(timezone.utc),
      scores = 0
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

  @staticmethod
  async def update_user(db: AsyncSession, token: str, update_data: UpdateUserForm) -> Type[User]:
    detached_user = await SecurityMiddleware.get_user_or_error_dict(token, db)
    user = await db.get(User, detached_user.id)

    if not detached_user or not user:
      raise NoResultFound("Пользователь не найден")

    for field, value in update_data.model_dump(exclude_unset=True).items():
      if isinstance(value, datetime) and value.tzinfo is not None:
        value = value.replace(tzinfo=None)
      setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

  @staticmethod
  async def update_user_for_admin(db: AsyncSession, user_data: UserPayload) -> Union[User, Dict[str, Any]]:
    user = await UserService.get_user_by_id(user_data.id, db)

    if not user:
      return ResponseUtils.error("Пользователя не существует!")

    user.name = user_data.name
    user.role = user_data.role
    user.phone_number = user_data.phone_number

    await db.commit()
    await db.refresh(user)

    return user

  @staticmethod
  async def delete_user_by_id(db: AsyncSession,
                              user_id: UUID) ->  Dict[str, Any]:
    user = await UserService.get_user_by_id(user_id, db)
    if not user:
      return ResponseUtils.error("Пользователя не существует!")
    await db.delete(user)
    await db.commit()
    return ResponseUtils.success(message="Пользователь удален")

  async def delete_user_by_token(db: AsyncSession,
                              token: str) -> Dict[str, Any]:
    detached_user = await SecurityMiddleware.get_user_or_error_dict(token, db)
    if not detached_user:
      return ResponseUtils.error("Пользователя не существует!")
    user = await db.get(User, detached_user.id)
    await db.delete(user)
    await db.commit()
    return ResponseUtils.success(message="Пользователь удален")

  @staticmethod
  async def check_users(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return len(users) > 0

  @staticmethod
  async def get_all_users(db: AsyncSession) -> List[User]:
    query = select(User)
    result = await db.execute(query)
    users = list(result.scalars().all())
    return users

  @staticmethod
  async def get_user_by_phone(db: AsyncSession, phone: str):
    result = await db.execute(select(User).where(User.phone_number == phone))
    user = result.scalar_one_or_none()
    return user