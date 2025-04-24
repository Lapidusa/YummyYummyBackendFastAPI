from typing import Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, EmailStr

class Roles(str, Enum):
  USER = 0
  ADMIN = 1
  COURIER = 2
  MANAGER = 3

class UpdateUserBase(BaseModel):
  phone_number: Optional[str]
  email: Optional[EmailStr]
  name: Optional[str]
  date_of_birth: Optional[datetime]
  image_url: Optional[str]

class Config:
  orm_mode = True
