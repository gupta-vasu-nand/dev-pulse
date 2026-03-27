"""Rate limiting utilities for GitHub API."""

import time
from typing import Optional
from functools import wraps

from dev_pulse.core.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 5000, window_seconds: int = 3600):
        """Initialize rate limiter."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Check if request can be made."""
        now = time.time()
        # Remove old requests
        self.requests = [r for r in self.requests if r > now - self.window_seconds]
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a request."""
        self.requests.append(time.time())
    
    def wait_if_needed(self):
        """Wait if rate limit is reached."""
        if not self.can_make_request():
            wait_time = self.window_seconds - (time.time() - self.requests[0])
            if wait_time > 0:
                logger.warning(f"Rate limit approaching, waiting {wait_time:.2f}s")
                time.sleep(wait_time)


def handle_rate_limits(func):
    """Decorator to handle rate limits."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        limiter = RateLimiter()
        limiter.wait_if_needed()
        result = func(*args, **kwargs)
        limiter.record_request()
        return result
    return wrapper