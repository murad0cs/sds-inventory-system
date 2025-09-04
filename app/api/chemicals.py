from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List
import asyncpg
import math
from app.db.session import get_db, get_asyncpg_connection
from app.models import Chemical, InventoryLog
from app.api import schemas
from app.services.audit_service import AuditService

router = APIRouter(prefix="/chemicals", tags=["chemicals"])

@router.post("/", response_model=schemas.Chemical)
async def create_chemical(
    chemical: schemas.ChemicalCreate,
    db: AsyncSession = Depends(get_db)
):
    db_chemical = Chemical(**chemical.dict())
    db.add(db_chemical)
    await db.flush()
    
    try:
        await AuditService.log_operation(
            db=db,
            table_name="chemicals",
            operation="CREATE",
            record_id=db_chemical.id,
            new_values=AuditService.serialize_model(db_chemical)
        )
    except Exception:
        pass
    
    await db.commit()
    await db.refresh(db_chemical)
    return db_chemical

@router.get("/", response_model=schemas.PaginatedResponse[schemas.Chemical])
async def read_chemicals(
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    
    skip = (page - 1) * page_size
    
    # Get total count
    count_result = await db.execute(select(func.count(Chemical.id)))
    total_count = count_result.scalar()
    
    # Get chemicals
    result = await db.execute(
        select(Chemical).offset(skip).limit(page_size)
    )
    chemicals = result.scalars().all()
    
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
    
    return {
        "items": chemicals,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }

@router.get("/{chemical_id}", response_model=schemas.Chemical)
async def read_chemical(
    chemical_id: int,
    conn: asyncpg.Connection = Depends(get_asyncpg_connection)
):
    query = """
        SELECT id, name, cas_number, quantity, unit, created_at, updated_at
        FROM chemicals
        WHERE id = $1
    """
    row = await conn.fetchrow(query, chemical_id)
    
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chemical with id {chemical_id} not found"
        )
    
    return dict(row)

@router.put("/{chemical_id}", response_model=schemas.Chemical)
async def update_chemical(
    chemical_id: int,
    chemical_update: schemas.ChemicalUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chemical).where(Chemical.id == chemical_id)
    )
    db_chemical = result.scalar_one_or_none()
    
    if db_chemical is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chemical with id {chemical_id} not found"
        )
    
    old_values = AuditService.serialize_model(db_chemical)
    
    update_data = chemical_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chemical, field, value)
    
    await db.flush()
    
    try:
        await AuditService.log_operation(
            db=db,
            table_name="chemicals",
            operation="UPDATE",
            record_id=chemical_id,
            old_values=old_values,
            new_values=AuditService.serialize_model(db_chemical)
        )
    except Exception:
        pass
    
    await db.commit()
    await db.refresh(db_chemical)
    return db_chemical

@router.delete("/{chemical_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chemical(
    chemical_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chemical).where(Chemical.id == chemical_id)
    )
    db_chemical = result.scalar_one_or_none()
    
    if db_chemical is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chemical with id {chemical_id} not found"
        )
    
    old_values = AuditService.serialize_model(db_chemical)
    
    await db.execute(
        delete(InventoryLog).where(InventoryLog.chemical_id == chemical_id)
    )
    
    try:
        await AuditService.log_operation(
            db=db,
            table_name="chemicals",
            operation="DELETE",
            record_id=chemical_id,
            old_values=old_values
        )
    except Exception:
        pass
    
    await db.execute(
        delete(Chemical).where(Chemical.id == chemical_id)
    )
    await db.commit()

@router.post("/{chemical_id}/log", response_model=schemas.InventoryLog)
async def create_inventory_log(
    chemical_id: int,
    log_entry: schemas.InventoryLogCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chemical).where(Chemical.id == chemical_id)
    )
    db_chemical = result.scalar_one_or_none()
    
    if db_chemical is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chemical with id {chemical_id} not found"
        )
    
    db_log = InventoryLog(
        chemical_id=chemical_id,
        **log_entry.dict()
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

@router.get("/{chemical_id}/logs", response_model=schemas.PaginatedResponse[schemas.InventoryLog])
async def read_inventory_logs(
    chemical_id: int,
    page: int = 1,
    page_size: int = 10,
    conn: asyncpg.Connection = Depends(get_asyncpg_connection)
):
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > 100:
        page_size = 100
    
    skip = (page - 1) * page_size
    
    # Check if chemical exists
    chemical_exists = await conn.fetchrow(
        "SELECT 1 FROM chemicals WHERE id = $1",
        chemical_id
    )
    if chemical_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chemical with id {chemical_id} not found"
        )
    
    # Get total count
    count_result = await conn.fetchval(
        "SELECT COUNT(*) FROM inventory_logs WHERE chemical_id = $1",
        chemical_id
    )
    total_count = count_result or 0
    
    # Get logs with pagination
    query = """
        SELECT id, chemical_id, action_type::text as action_type, quantity, timestamp
        FROM inventory_logs
        WHERE chemical_id = $1
        ORDER BY timestamp DESC
        LIMIT $2 OFFSET $3
    """
    rows = await conn.fetch(query, chemical_id, page_size, skip)
    
    logs = []
    for row in rows:
        log_dict = dict(row)
        if log_dict.get('action_type'):
            log_dict['action_type'] = log_dict['action_type'].lower()
        logs.append(log_dict)
    
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
    
    return {
        "items": logs,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }
