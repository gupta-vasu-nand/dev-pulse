"""Database connection management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
import json

from dev_pulse.core.config import config
from dev_pulse.core.logger import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        self.db_path = db_path or config.db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema."""
        with self.get_connection() as conn:
            # Create cache table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    params TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            
            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_key 
                ON cache(cache_key)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON cache(expires_at)
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at < datetime('now')"
            )
            conn.commit()
            deleted = cursor.rowcount
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} expired cache entries")
            return deleted


database = Database()