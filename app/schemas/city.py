from uuid import UUID

from pydantic import BaseModel, Field

class City(BaseModel):

  name: str = Field(..., description="Название города")

  class Config:
    from_attributes = True

class CreateCity(City):
  pass

class UpdateCity(City):
  id: UUID = Field(..., description="Уникальный идентификатор города")
  pass