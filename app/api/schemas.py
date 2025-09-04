from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from app.models.inventory_log import ActionType

T = TypeVar('T')


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


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class AuditLog(BaseModel):
    id: int
    table_name: str
    operation: str
    record_id: int
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    timestamp: datetime
    user_info: Optional[str] = None
    
    class Config:
        from_attributes = True