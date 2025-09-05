from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False, index=True)
    operation = Column(String, nullable=False, index=True)  # CREATE, UPDATE, DELETE
    record_id = Column(Integer, nullable=False, index=True)
    old_values = Column(Text, nullable=True)  # JSON string of old values
    new_values = Column(Text, nullable=True)  # JSON string of new values
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_info = Column(String, nullable=True)  # Can track user/session info later