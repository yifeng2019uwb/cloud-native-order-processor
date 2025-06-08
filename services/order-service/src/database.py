import sys
import os

from database import DatabaseManager, get_db

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "common"))


# Re-export for local use
db_manager = DatabaseManager()

__all__ = ["db_manager", "get_db"]
