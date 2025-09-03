from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Chemical(Base):
    __tablename__ = "chemicals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cas_number = Column(String, unique=True, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())