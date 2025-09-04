import logging
import logging.handlers
import os
from datetime import datetime
import json
from pathlib import Path


def setup_logging():
    """Configure file-based logging for the application"""
    
    # Create logs directory - handle both Docker and local paths
    if os.path.exists("/app/logs"):
        log_dir = Path("/app/logs")
    else:
        log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Create formatters
    json_formatter = JsonFormatter()
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove default handlers
    root_logger.handlers = []
    
    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(standard_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # 2. General Application Log File (Rotating)
    app_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_file_handler.setFormatter(standard_formatter)
    app_file_handler.setLevel(logging.INFO)
    root_logger.addHandler(app_file_handler)
    
    # 3. Error Log File
    error_file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_file_handler.setFormatter(standard_formatter)
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)
    
    # 4. Audit Log File (JSON format, daily rotation)
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False
    
    audit_file_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / "audit.json",
        when="midnight",
        interval=1,
        backupCount=30
    )
    audit_file_handler.setFormatter(json_formatter)
    audit_logger.addHandler(audit_file_handler)
    
    # 5. Chemical Operations Log
    chemical_logger = logging.getLogger("chemicals")
    chemical_logger.setLevel(logging.INFO)
    
    chemical_file_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / "chemicals.log",
        when="midnight",
        interval=1,
        backupCount=30
    )
    chemical_file_handler.setFormatter(standard_formatter)
    chemical_logger.addHandler(chemical_file_handler)
    
    return root_logger


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'table_name'):
            log_obj['table_name'] = record.table_name
        if hasattr(record, 'operation'):
            log_obj['operation'] = record.operation
        if hasattr(record, 'record_id'):
            log_obj['record_id'] = record.record_id
        if hasattr(record, 'old_values'):
            log_obj['old_values'] = record.old_values
        if hasattr(record, 'new_values'):
            log_obj['new_values'] = record.new_values
        
        return json.dumps(log_obj)