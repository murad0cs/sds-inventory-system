import os
from datetime import datetime
from pathlib import Path
import json


class SimpleFileLogger:
    def __init__(self):
        # Ensure logs directory exists
        try:
            self.log_dir = Path("/app/logs")
            self.log_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            print(f"Warning: Could not create log directory: {e}")
            # Fall back to current directory
            self.log_dir = Path(".")
        
    def log_audit(self, operation, table_name, record_id, old_values=None, new_values=None):
        """Write audit log to file"""
        timestamp = datetime.now().isoformat()
        
        # Write to audit.log
        audit_entry = {
            "timestamp": timestamp,
            "operation": operation,
            "table_name": table_name,
            "record_id": record_id,
            "old_values": old_values,
            "new_values": new_values
        }
        
        try:
            # Append to audit.json
            with open(self.log_dir / "audit.json", "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
            
            # Append to audit.log in readable format
            with open(self.log_dir / "audit.log", "a") as f:
                f.write(f"[{timestamp}] {operation} on {table_name} ID:{record_id}\n")
            
            # Chemical-specific log
            if table_name == "chemicals":
                with open(self.log_dir / "chemicals.log", "a") as f:
                    f.write(f"[{timestamp}] {operation} Chemical ID:{record_id}")
                    if new_values and 'name' in new_values:
                        f.write(f" - Name: {new_values['name']}")
                    f.write("\n")
                    
        except Exception as e:
            print(f"Error writing to log file: {e}")


# Global logger instance - lazy initialization
_file_logger = None

def get_file_logger():
    global _file_logger
    if _file_logger is None:
        _file_logger = SimpleFileLogger()
    return _file_logger

file_logger = get_file_logger