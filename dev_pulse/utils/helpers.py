"""Helper utilities for Dev-Pulse."""

from datetime import datetime, timedelta
from typing import Optional
import re


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime."""
    if not date_str:
        return None
    
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        # Try common formats
        for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None


def format_date(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def validate_repo(repo: str) -> bool:
    """Validate repository format (owner/repo)."""
    pattern = r'^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$'
    return bool(re.match(pattern, repo))


def get_default_since() -> datetime:
    """Get default since date (30 days ago)."""
    return datetime.now() - timedelta(days=30)