from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import math
from app.db.session import get_db
from app.models import AuditLog
from app.api import schemas

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/logs", response_model=schemas.PaginatedResponse[schemas.AuditLog])
async def get_audit_logs(
    table_name: Optional[str] = None,
    operation: Optional[str] = None,
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
    
    # Build query
    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))
    
    if table_name:
        query = query.where(AuditLog.table_name == table_name)
        count_query = count_query.where(AuditLog.table_name == table_name)
    if operation:
        query = query.where(AuditLog.operation == operation)
        count_query = count_query.where(AuditLog.operation == operation)
    
    # Get total count
    count_result = await db.execute(count_query)
    total_count = count_result.scalar() or 0
    
    # Get logs with pagination
    query = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    
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

@router.get("/logs/record/{record_id}", response_model=schemas.PaginatedResponse[schemas.AuditLog])
async def get_audit_logs_by_record(
    record_id: int,
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
    count_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.record_id == record_id)
    )
    total_count = count_result.scalar() or 0
    
    # Get logs
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.record_id == record_id)
        .order_by(AuditLog.timestamp.desc())
        .offset(skip)
        .limit(page_size)
    )
    logs = result.scalars().all()
    
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