import json
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog
# from app.core.simple_logger import file_logger  # Temporarily disabled

audit_logger = logging.getLogger("audit")
chemical_logger = logging.getLogger("chemicals")


class AuditService:
    @staticmethod
    async def log_operation(
        db: AsyncSession,
        table_name: str,
        operation: str,
        record_id: int,
        old_values: Optional[Dict[Any, Any]] = None,
        new_values: Optional[Dict[Any, Any]] = None,
        user_info: Optional[str] = None
    ):
        # Create database entry
        audit_log = AuditLog(
            table_name=table_name,
            operation=operation,
            record_id=record_id,
            old_values=json.dumps(old_values, default=str) if old_values else None,
            new_values=json.dumps(new_values, default=str) if new_values else None,
            user_info=user_info
        )
        db.add(audit_log)
        await db.flush()
        
        # File logging temporarily disabled to fix API
        # Will re-enable after fixing initialization issue
        pass
        
        return audit_log
    
    @staticmethod
    def serialize_model(model_instance) -> Dict[Any, Any]:
        if not model_instance:
            return {}
        
        result = {}
        for column in model_instance.__table__.columns:
            try:
                value = getattr(model_instance, column.name, None)
                if value is not None:
                    result[column.name] = str(value) if not isinstance(value, (str, int, float, bool)) else value
            except Exception:
                continue
        return result