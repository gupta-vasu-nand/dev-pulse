"""Metrics aggregation service for GitHub activity."""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
import time

from dev_pulse.core.logger import get_logger
from dev_pulse.services.github_client import github_client

logger = get_logger(__name__)


class MetricsService:
    """Service for aggregating developer metrics."""
    
    def __init__(self):
        """Initialize metrics service."""
        pass
    
    def analyze_activity(self, repo: str, since: Optional[datetime] = None, user: Optional[str] = None) -> Dict:
        """Analyze developer activity for a repository."""
        logger.info(f"Analyzing activity for {repo}")
        
        # Fetch data
        commits = github_client.get_commits(repo, since)
        pull_requests = github_client.get_pull_requests(repo)
        
        logger.info(f"Fetched {len(commits)} commits and {len(pull_requests)} PRs")
        
        # Initialize metrics
        metrics = defaultdict(lambda: {
            'commits': 0,
            'prs_opened': 0,
            'prs_merged': 0,
            'reviews': 0,
            'review_comments': 0
        })
        
        # Process commits
        for commit in commits:
            author = None
            # Try different fields for author name
            if commit.get('author') and commit['author'].get('login'):
                author = commit['author']['login']
            elif commit.get('commit', {}).get('author', {}).get('name'):
                author = commit['commit']['author']['name']
            elif commit.get('commit', {}).get('committer', {}).get('name'):
                author = commit['commit']['committer']['name']
            else:
                author = 'unknown'
            
            if user and user.lower() not in author.lower():
                continue
            
            metrics[author]['commits'] += 1
        
        # Process pull requests - limit to avoid excessive API calls
        pr_count = 0
        max_prs_to_process = 50  # Only process first 50 PRs for performance
        
        for pr in pull_requests:
            pr_count += 1
            if pr_count > max_prs_to_process:
                logger.info(f"Stopped after processing {max_prs_to_process} PRs (out of {len(pull_requests)})")
                break
            
            creator = pr.get('user', {}).get('login', 'unknown')
            
            if user and user.lower() not in creator.lower():
                continue
            
            metrics[creator]['prs_opened'] += 1
            
            # Check if merged
            if pr.get('merged_at'):
                metrics[creator]['prs_merged'] += 1
            
            # Only fetch reviews for PRs that might have them (skip if no reviews likely)
            # This is a performance optimization
            review_count = pr.get('review_comments', 0) + pr.get('comments', 0)
            if review_count > 0 or pr_count < 20:  # Check first 20 PRs regardless
                # Get reviews and comments
                try:
                    reviews = github_client.get_reviews(repo, pr['number'])
                    for review in reviews:
                        if review and review.get('user'):
                            reviewer = review['user'].get('login', 'unknown')
                            if not user or user.lower() in reviewer.lower():
                                metrics[reviewer]['reviews'] += 1
                    
                    comments = github_client.get_pr_comments(repo, pr['number'])
                    for comment in comments:
                        if comment and comment.get('user'):
                            commenter = comment['user'].get('login', 'unknown')
                            if not user or user.lower() in commenter.lower():
                                metrics[commenter]['review_comments'] += 1
                        
                except Exception as e:
                    logger.error(f"Error fetching reviews for PR #{pr['number']}: {e}")
            
            # Small delay between PR processing
            time.sleep(0.1)
        
        # Filter by user if specified
        if user:
            metrics = {k: v for k, v in metrics.items() if user.lower() in k.lower()}
        
        # Remove unknown users if they have no activity
        metrics = {k: v for k, v in metrics.items() if k != 'unknown' or sum(v.values()) > 0}
        
        logger.info(f"Analysis complete: found {len(metrics)} contributors")
        
        return {
            'repository': repo,
            'since': since.isoformat() if since else None,
            'metrics': dict(metrics),
            'total_contributors': len(metrics),
            'prs_processed': min(pr_count, max_prs_to_process),
            'total_prs': len(pull_requests)
        }
    
    def get_summary(self, metrics: Dict) -> Dict:
        """Get summary statistics from metrics."""
        total_commits = sum(m['commits'] for m in metrics['metrics'].values())
        total_prs_opened = sum(m['prs_opened'] for m in metrics['metrics'].values())
        total_prs_merged = sum(m['prs_merged'] for m in metrics['metrics'].values())
        total_reviews = sum(m['reviews'] for m in metrics['metrics'].values())
        total_comments = sum(m['review_comments'] for m in metrics['metrics'].values())
        
        return {
            'total_commits': total_commits,
            'total_prs_opened': total_prs_opened,
            'total_prs_merged': total_prs_merged,
            'total_reviews': total_reviews,
            'total_comments': total_comments,
            'total_contributors': metrics['total_contributors'],
            'prs_processed': metrics.get('prs_processed', 0),
            'total_prs': metrics.get('total_prs', 0)
        }


# Create a singleton instance
metrics_service = MetricsService()