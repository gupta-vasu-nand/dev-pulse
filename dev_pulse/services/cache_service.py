"""Cache service for storing GitHub API responses."""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from dev_pulse.core.config import config
from dev_pulse.core.logger import get_logger
from dev_pulse.db.database import database

logger = get_logger(__name__)


class CacheService:
    """Service for managing API response caching."""
    
    def __init__(self):
        """Initialize cache service."""
        self.ttl_hours = config.cache_ttl_hours
    
    def _generate_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate unique cache key for request."""
        key_string = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve cached data."""
        cache_key = self._generate_cache_key(endpoint, params)
        
        try:
            with database.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT data FROM cache WHERE cache_key = ? AND expires_at > datetime('now')",
                    (cache_key,)
                )
                row = cursor.fetchone()
                
                if row:
                    logger.info(f"Cache HIT for {endpoint}")
                    return json.loads(row['data'])
                
                logger.info(f"Cache MISS for {endpoint}")
                return None
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
            return None
    
    def set(self, endpoint: str, params: Dict[str, Any], data: Dict[str, Any]):
        """Store data in cache."""
        cache_key = self._generate_cache_key(endpoint, params)
        expires_at = datetime.now() + timedelta(hours=self.ttl_hours)
        
        try:
            with database.get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache (cache_key, data, endpoint, params, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        cache_key,
                        json.dumps(data),
                        endpoint,
                        json.dumps(params),
                        expires_at.isoformat()
                    )
                )
                conn.commit()
                logger.info(f"Cached data for {endpoint} (expires in {self.ttl_hours}h)")
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")
    
    def clear(self, endpoint: Optional[str] = None) -> int:
        """Clear cache entries."""
        try:
            with database.get_connection() as conn:
                if endpoint:
                    cursor = conn.execute(
                        "DELETE FROM cache WHERE endpoint = ?",
                        (endpoint,)
                    )
                else:
                    cursor = conn.execute("DELETE FROM cache")
                
                conn.commit()
                deleted = cursor.rowcount
                logger.info(f"Cleared {deleted} cache entries")
                return deleted
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        try:
            with database.get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE expires_at < datetime('now')"
                )
                conn.commit()
                deleted = cursor.rowcount
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} expired cache entries")
                return deleted
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get cache status information."""
        try:
            with database.get_connection() as conn:
                # Total entries
                cursor = conn.execute("SELECT COUNT(*) as total FROM cache")
                total = cursor.fetchone()['total']
                
                # Expired entries
                cursor = conn.execute(
                    "SELECT COUNT(*) as expired FROM cache WHERE expires_at < datetime('now')"
                )
                expired = cursor.fetchone()['expired']
                
                # By endpoint
                cursor = conn.execute(
                    "SELECT endpoint, COUNT(*) as count FROM cache GROUP BY endpoint"
                )
                by_endpoint = {row['endpoint']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'total_entries': total,
                    'expired_entries': expired,
                    'by_endpoint': by_endpoint,
                    'ttl_hours': self.ttl_hours
                }
        except Exception as e:
            logger.error(f"Error getting cache status: {e}")
            return {
                'total_entries': 0,
                'expired_entries': 0,
                'by_endpoint': {},
                'ttl_hours': self.ttl_hours,
                'error': str(e)
            }


# Create a singleton instance
cache_service = CacheService()