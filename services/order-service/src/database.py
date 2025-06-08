import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'common'))

from database import DatabaseManager, get_db

# Re-export for local use
db_manager = DatabaseManager()

__all__ = ["db_manager", "get_db"]