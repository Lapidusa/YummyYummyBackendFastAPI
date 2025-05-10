from typing import Any, Type, Coroutine

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from app.core.security import SecurityMiddleware
from app.db.models.users import User, Roles
from app.schemas.user import UpdateUserBase


class UserService:
  async def create_new_user(db: AsyncSession, phone_number: str) -> User:
    new_user = User(
      id = uuid.uuid4(),
      phone_number = phone_number,
      role = Roles.USER,
      created_at = datetime.utcnow(),
      scores = 0
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

  @staticmethod
  async def update_user(db: AsyncSession, token: str, update_data: UpdateUserBase) -> Type[User]:
    detached_user = await SecurityMiddleware.get_user_or_error_dict(token, db)
    user = await db.get(User, detached_user.id)
    if not detached_user:
      raise NoResultFound("Пользователь не найден")
    if not user:
      raise NoResultFound("Пользователь не найден")
    for field, value in update_data.dict(exclude_unset=True).items():
      if isinstance(value, datetime) and value.tzinfo is not None:
        value = value.replace(tzinfo=None)
      setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

  @staticmethod
  async def check_users(db: AsyncSession):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return len(users) > 0

  @staticmethod
  async def get_user_by_phone(db: AsyncSession, phone: str):
    result = await db.execute(select(User).where(User.phone_number == phone))
    user = result.scalar_one_or_none()
    return user