"""Tests for metrics service."""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from dev_pulse.services.metrics_service import MetricsService


class TestMetricsService(unittest.TestCase):
    """Test metrics aggregation."""
    
    def setUp(self):
        self.service = MetricsService()
    
    @patch('dev_pulse.services.metrics_service.github_client')
    def test_analyze_activity(self, mock_github):
        """Test activity analysis."""
        # Mock data
        mock_github.get_commits.return_value = [
            {'commit': {'author': {'name': 'alice'}}},
            {'commit': {'author': {'name': 'bob'}}},
            {'commit': {'author': {'name': 'alice'}}}
        ]
        
        mock_github.get_pull_requests.return_value = [
            {
                'number': 1,
                'user': {'login': 'alice'},
                'merged_at': '2024-01-01'
            }
        ]
        
        mock_github.get_reviews.return_value = [
            {'user': {'login': 'bob'}}
        ]
        
        mock_github.get_pr_comments.return_value = []
        
        # Run analysis
        result = self.service.analyze_activity(
            'test/repo',
            since=datetime(2024, 1, 1)
        )
        
        # Verify results
        self.assertEqual(result['total_contributors'], 2)
        self.assertEqual(result['metrics']['alice']['commits'], 2)
        self.assertEqual(result['metrics']['bob']['commits'], 1)
        self.assertEqual(result['metrics']['alice']['prs_opened'], 1)
    
    def test_get_summary(self):
        """Test summary generation."""
        metrics = {
            'repository': 'test/repo',
            'total_contributors': 2,
            'metrics': {
                'alice': {
                    'commits': 10,
                    'prs_opened': 5,
                    'prs_merged': 3,
                    'reviews': 2,
                    'review_comments': 5
                },
                'bob': {
                    'commits': 7,
                    'prs_opened': 3,
                    'prs_merged': 2,
                    'reviews': 1,
                    'review_comments': 2
                }
            }
        }
        
        summary = self.service.get_summary(metrics)
        
        self.assertEqual(summary['total_commits'], 17)
        self.assertEqual(summary['total_prs_opened'], 8)
        self.assertEqual(summary['total_prs_merged'], 5)
        self.assertEqual(summary['total_reviews'], 3)


if __name__ == '__main__':
    unittest.main()