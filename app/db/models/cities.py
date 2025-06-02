import uuid

from geoalchemy2 import Geometry
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db import Base

class City(Base):
    __tablename__ = 'cities'

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    point = Column(Geometry('POINT'), nullable=False)
    stores = relationship("Store", back_populates="city")
