from typing import Optional
from datetime import datetime
from uuid import UUID
from fastapi.params import Form
from pydantic import BaseModel, EmailStr

from app.db.models.users import Roles

class UserPayload(BaseModel):
  phone_number: str
  name: str
  role: Roles

class UserPayloadWithId(UserPayload):
  id: UUID
  pass

class UpdateUserForm(BaseModel):
  phone_number: Optional[str]
  email: Optional[EmailStr] = None
  name: Optional[str] = None
  date_of_birth: Optional[datetime] = None
  image_url: Optional[str] = None

  @classmethod
  def as_form(
      cls,
      phone_number: Optional[str] = Form(None),
      email: Optional[EmailStr] = Form(None),
      name: Optional[str] = Form(None),
      date_of_birth: Optional[datetime] = Form(None)
  ):
    return cls(
      phone_number=phone_number,
      email=email,
      name=name,
      date_of_birth=date_of_birth
    )

class Config:
  orm_mode = True
