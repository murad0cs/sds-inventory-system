from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.inventory_log import ActionType


class ChemicalBase(BaseModel):
    name: str
    cas_number: str
    quantity: float
    unit: str


class ChemicalCreate(ChemicalBase):
    pass


class ChemicalUpdate(BaseModel):
    name: Optional[str] = None
    cas_number: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None


class Chemical(ChemicalBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InventoryLogBase(BaseModel):
    action_type: ActionType
    quantity: float


class InventoryLogCreate(InventoryLogBase):
    pass


class InventoryLog(InventoryLogBase):
    id: int
    chemical_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True