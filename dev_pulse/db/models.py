"""Database models for Dev-Pulse."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class CacheEntry:
    """Cache entry model."""
    id: Optional[int] = None
    cache_key: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    endpoint: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'data': json.dumps(self.data) if self.data else None,
            'endpoint': self.endpoint,
            'params': json.dumps(self.params) if self.params else None,
            'created_at': self.created_at,
            'expires_at': self.expires_at
        }
    
    @classmethod
    def from_row(cls, row) -> 'CacheEntry':
        """Create from database row."""
        return cls(
            id=row['id'],
            cache_key=row['cache_key'],
            data=json.loads(row['data']) if row['data'] else None,
            endpoint=row['endpoint'],
            params=json.loads(row['params']) if row['params'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None
        )