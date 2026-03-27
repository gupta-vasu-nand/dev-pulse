"""GitHub REST API client with caching and rate limiting."""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from dev_pulse.core.config import config
from dev_pulse.core.logger import get_logger
from dev_pulse.services.cache_service import cache_service

logger = get_logger(__name__)


class GitHubClient:
    """GitHub API client with caching and rate limiting."""
    
    def __init__(self):
        """Initialize GitHub client."""
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {config.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Dev-Pulse/1.0.0'
        })
        self.base_url = config.github_api_base
        self.request_count = 0
        self.last_request_time = 0
    
    def _rate_limit_sleep(self):
        """Implement rate limiting to avoid hitting API limits."""
        current_time = time.time()
        # Ensure at least 0.5 seconds between requests
        if current_time - self.last_request_time < 0.5:
            time.sleep(0.5 - (current_time - self.last_request_time))
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with caching and error handling."""
        params = params or {}
        
        # Check cache
        cached_data = cache_service.get(endpoint, params)
        if cached_data:
            return cached_data
        
        # Rate limit
        self._rate_limit_sleep()
        
        # Make API request
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Fetching {url}")
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self.request_count += 1
            
            # Check rate limit
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 100:
                logger.warning(f"Rate limit low: {remaining} requests remaining")
            
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                logger.warning("Rate limit exceeded")
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                if reset_time:
                    wait_time = reset_time - time.time()
                    if wait_time > 0:
                        logger.info(f"Waiting {wait_time:.0f}s for rate limit reset")
                        time.sleep(wait_time + 1)
                        return self._make_request(endpoint, params)
            
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            cache_service.set(endpoint, params, data)
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def _paginate(self, endpoint: str, params: Optional[Dict] = None, max_pages: int = 3) -> List[Dict]:
        """Handle paginated API responses with page limit."""
        all_items = []
        page = 1
        per_page = 50  # Reduced from 100 to be gentler on rate limits
        
        while page <= max_pages:
            params = params or {}
            params['page'] = page
            params['per_page'] = per_page
            
            logger.debug(f"Fetching page {page} from {endpoint}")
            data = self._make_request(endpoint, params)
            
            if not data:
                logger.debug(f"No data returned for page {page}, stopping")
                break
            
            if isinstance(data, list):
                if not data:
                    logger.debug(f"Empty list for page {page}, stopping")
                    break
                    
                all_items.extend(data)
                logger.debug(f"Page {page}: got {len(data)} items, total: {len(all_items)}")
                
                # If we got less than per_page, this is the last page
                if len(data) < per_page:
                    logger.debug(f"Last page reached (got {len(data)} < {per_page})")
                    break
            else:
                # Single item response
                all_items.append(data)
                break
            
            page += 1
        
        logger.info(f"Fetched {len(all_items)} items from {endpoint}")
        return all_items
    
    def get_commits(self, repo: str, since: Optional[datetime] = None) -> List[Dict]:
        """Get commits for a repository."""
        params = {}
        if since:
            params['since'] = since.isoformat()
        
        try:
            return self._paginate(f"/repos/{repo}/commits", params, max_pages=3)
        except Exception as e:
            logger.error(f"Failed to fetch commits for {repo}: {e}")
            return []
    
    def get_pull_requests(self, repo: str, state: str = 'all') -> List[Dict]:
        """Get pull requests for a repository."""
        params = {
            'state': state,
            'sort': 'updated',
            'direction': 'desc'
        }
        try:
            # Only get recent PRs (max 150 = 3 pages of 50)
            return self._paginate(f"/repos/{repo}/pulls", params, max_pages=3)
        except Exception as e:
            logger.error(f"Failed to fetch PRs for {repo}: {e}")
            return []
    
    def get_reviews(self, repo: str, pr_number: int) -> List[Dict]:
        """Get reviews for a pull request."""
        try:
            return self._paginate(f"/repos/{repo}/pulls/{pr_number}/reviews", max_pages=2)
        except Exception as e:
            logger.error(f"Failed to fetch reviews for PR #{pr_number}: {e}")
            return []
    
    def get_pr_comments(self, repo: str, pr_number: int) -> List[Dict]:
        """Get comments for a pull request."""
        try:
            return self._paginate(f"/repos/{repo}/pulls/{pr_number}/comments", max_pages=2)
        except Exception as e:
            logger.error(f"Failed to fetch comments for PR #{pr_number}: {e}")
            return []


# Create a singleton instance
github_client = GitHubClient()