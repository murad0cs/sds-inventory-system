from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List
import asyncpg
from app.db.session import get_db, get_asyncpg_connection
from app.models import Chemical, InventoryLog, ActionType
from app.api import schemas

router = APIRouter(prefix="/chemicals", tags=["chemicals"])


@router.post("/", response_model=schemas.Chemical)
async def create_chemical(
    chemical: schemas.ChemicalCreate,
    db: AsyncSession = Depends(get_db)
):
    db_chemical = Chemical(**chemical.dict())
    db.add(db_chemical)
    await db.commit()
    await db.refresh(db_chemical)
    return db_chemical


@router.get("/", response_model=List[schemas.Chemical])
async def read_chemicals(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chemical).offset(skip).limit(limit)
    )
    chemicals = result.scalars().all()
    return chemicals


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
    
    update_data = chemical_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_chemical, field, value)
    
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
    
    await db.execute(
        delete(InventoryLog).where(InventoryLog.chemical_id == chemical_id)
    )
    
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


@router.get("/{chemical_id}/logs", response_model=List[schemas.InventoryLog])
async def read_inventory_logs(
    chemical_id: int,
    conn: asyncpg.Connection = Depends(get_asyncpg_connection)
):
    query = """
        SELECT id, chemical_id, action_type::text as action_type, quantity, timestamp
        FROM inventory_logs
        WHERE chemical_id = $1
        ORDER BY timestamp DESC
    """
    rows = await conn.fetch(query, chemical_id)
    
    if not rows:
        result = await conn.fetchrow(
            "SELECT 1 FROM chemicals WHERE id = $1",
            chemical_id
        )
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chemical with id {chemical_id} not found"
            )
    
    logs = []
    for row in rows:
        log_dict = dict(row)
        if log_dict.get('action_type'):
            log_dict['action_type'] = log_dict['action_type'].lower()
        logs.append(log_dict)
    
    return logs