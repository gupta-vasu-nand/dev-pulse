I'll add comprehensive test commands to the README. Here's the updated README with the test commands section:

# Dev-Pulse

A powerful CLI tool that analyzes GitHub developer activity across repositories, providing insights into commits, pull requests, and code reviews.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Analyze Repository Activity](#analyze-repository-activity)
  - [Cache Management](#cache-management)
  - [Help Commands](#help-commands)
- [Command Reference](#command-reference)
- [Output Examples](#output-examples)
- [Project Structure](#project-structure)
- [Logging System](#logging-system)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)
- [Testing](#testing)
- [Development](#development)
- [License](#license)

## Features

- **Comprehensive Metrics**: Track commits, PRs opened/merged, code reviews, and review comments
- **Smart Caching**: SQLite-based caching system to reduce API calls and improve performance
- **Structured Logging**: Detailed logging with daily rotation and multiple log levels
- **Rich Terminal Output**: Beautiful tables, progress indicators, and color-coded output
- **Rate Limit Handling**: Automatic handling of GitHub API rate limits with exponential backoff
- **User Filtering**: Filter analysis by specific developers or partial username matches
- **Date Range Filtering**: Analyze activity since a specific date
- **Performance Controls**: Limit the number of PRs processed for large repositories
- **Cache Management**: View cache status and clear cache for specific endpoints

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning the repository)
- GitHub Personal Access Token

### Step 1: Clone the Repository

```bash
git clone https://github.com/gupta-vasu-nand/dev-pulse.git
cd dev-pulse
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your GitHub token:

```
GITHUB_TOKEN=enter_your_own_github_personal_access_token_here
CACHE_TTL_HOURS=24
DB_PATH=dev_pulse.db
LOG_DIR=logs
LOG_LEVEL=INFO
MAX_RETRIES=3
RETRY_DELAY=1
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| GITHUB_TOKEN | GitHub Personal Access Token | None | Yes |
| CACHE_TTL_HOURS | Cache time-to-live in hours | 24 | No |
| DB_PATH | SQLite database file path | dev_pulse.db | No |
| LOG_DIR | Directory for log files | logs | No |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO | No |
| MAX_RETRIES | Maximum retry attempts for failed requests | 3 | No |
| RETRY_DELAY | Delay between retries in seconds | 1 | No |

### GitHub Token

To generate a GitHub Personal Access Token:

1. Navigate to GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Dev-Pulse")
4. Select scopes:
   - `repo` (for private repositories)
   - `public_repo` (for public repositories only)
   - `read:user` (for user information)
5. Click "Generate token" and copy the token immediately

## Usage

### Analyze Repository Activity

The `analyze` command is the main command for analyzing developer activity.

#### Basic Analysis

```bash
python -m dev_pulse.main analyze --repo owner/repo
```

#### Analysis with Date Filter

```bash
python -m dev_pulse.main analyze --repo owner/repo --since 2024-01-01
```

#### Analysis with User Filter

```bash
python -m dev_pulse.main analyze --repo owner/repo --user username
```

#### Analysis with All Options

```bash
python -m dev_pulse.main analyze --repo owner/repo --user username --since 2024-01-01 --max-prs 50
```

### Cache Management

#### View Cache Status

```bash
python -m dev_pulse.main cache-status
```

This command shows:
- Total number of cached entries
- Number of expired entries
- Cache TTL (Time To Live)
- Breakdown by API endpoint

#### Clear Entire Cache

```bash
python -m dev_pulse.main clear-cache
```

#### Clear Specific Endpoint Cache

```bash
python -m dev_pulse.main clear-cache --endpoint /repos/owner/repo/commits
```

### Help Commands

#### Main Help

```bash
python -m dev_pulse.main --help
```

#### Analyze Command Help

```bash
python -m dev_pulse.main analyze --help
```

## Command Reference

### analyze

Analyzes developer activity for a GitHub repository.

**Syntax:**
```bash
python -m dev_pulse.main analyze --repo REPO [OPTIONS]
```

**Options:**

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--repo` | Repository in format `owner/repo` | Yes | None |
| `--user` | Filter by username (partial match, case-insensitive) | No | None |
| `--since` | Start date in YYYY-MM-DD format | No | 30 days ago |
| `--max-prs` | Maximum number of pull requests to analyze | No | 50 |

**Examples:**

```bash
# Analyze all activity from the last 30 days
python -m dev_pulse.main analyze --repo octocat/Hello-World

# Analyze activity since January 1, 2024
python -m dev_pulse.main analyze --repo pandas-dev/pandas --since 2024-01-01

# Filter by specific user
python -m dev_pulse.main analyze --repo facebook/react --user dan --since 2024-03-01

# Limit PR analysis for performance
python -m dev_pulse.main analyze --repo kubernetes/kubernetes --max-prs 30
```

### cache-status

Displays cache statistics and cleans up expired entries.

**Syntax:**
```bash
python -m dev_pulse.main cache-status
```

**Output Information:**
- Total number of cached entries
- Number of expired entries
- Cache TTL in hours
- Count of entries per endpoint

### clear-cache

Clears cached data from the SQLite database.

**Syntax:**
```bash
python -m dev_pulse.main clear-cache [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--endpoint` | Clear cache for specific endpoint only | None (clears all) |

**Examples:**

```bash
# Clear all cache
python -m dev_pulse.main clear-cache

# Clear cache for specific endpoint
python -m dev_pulse.main clear-cache --endpoint /repos/octocat/Hello-World/commits
```

## Output Examples

### Summary Statistics

```
╭─────────────────────────────── Dev-Pulse Analysis ────────────────────────────────╮
│ Analyzing Repository: pandas-dev/pandas                                          │
│ Since: 2026-03-01                                                                │
│ User Filter: All users                                                           │
│ Max PRs: 50                                                                      │
╰───────────────────────────────────────────────────────────────────────────────────╯

Summary Statistics:
┌──────────────────────┬───────┐
│ Metric               │ Value │
├──────────────────────┼───────┤
│ Total Commits        │ 245   │
│ PRs Opened           │ 42    │
│ PRs Merged           │ 35    │
│ Code Reviews         │ 78    │
│ Review Comments      │ 156   │
│ Contributors         │ 12    │
│ Note                 │ Analyzed 50 of 347 PRs for performance │
└──────────────────────┴───────┘
```

### Detailed Developer Metrics

```
Detailed Developer Metrics:
┌─────────────────┬─────────┬───────────┬────────────┬─────────┬──────────┐
│ Developer       │ Commits │ PRs Opened│ PRs Merged │ Reviews │ Comments │
├─────────────────┼─────────┼───────────┼────────────┼─────────┼──────────┤
│ jreback         │ 67      │ 12        │ 10         │ 15      │ 42       │
│ williamahern    │ 45      │ 8         │ 7          │ 12      │ 28       │
│ mroeschke       │ 38      │ 6         │ 5          │ 9       │ 21       │
│ phofl           │ 29      │ 5         │ 4          │ 7       │ 18       │
│ rhshadrach      │ 24      │ 4         │ 3          │ 6       │ 15       │
│ ... and 7 more contributors                                                  │
└─────────────────┴─────────┴───────────┴────────────┴─────────┴──────────┘
```

### Cache Status

```
╭────────────────────────────────── Cache Status ──────────────────────────────────╮
│ Cache Status                                                                    │
│                                                                                 │
│ Total Entries: 127                                                              │
│ Expired Entries: 8                                                              │
│ TTL: 24 hours                                                                   │
│                                                                                 │
│ By Endpoint:                                                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│   • /repos/pandas-dev/pandas/commits: 3 entries                                 │
│   • /repos/pandas-dev/pandas/pulls: 3 entries                                   │
│   • /repos/pandas-dev/pandas/pulls/1/reviews: 1 entries                         │
│   • /repos/pandas-dev/pandas/pulls/1/comments: 1 entries                        │
│   ... and 119 more endpoints                                                    │
│                                                                                 │
│ Cleaned up 8 expired entries                                                    │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

## Project Structure

```
dev-pulse/
│
├── dev_pulse/                     # Main package
│   ├── __init__.py                # Package initialization
│   ├── main.py                    # CLI entry runner
│   │
│   ├── cli/                       # CLI interface
│   │   ├── __init__.py
│   │   └── main.py                # Click commands
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   └── logger.py              # Centralized logging system
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── github_client.py       # GitHub API client
│   │   ├── metrics_service.py     # Metrics aggregation
│   │   └── cache_service.py       # Cache management
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── database.py            # SQLite connection
│   │   └── models.py              # Schema definitions
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── helpers.py             # Helper functions
│       └── rate_limiter.py        # Rate limiting utilities
│
├── tests/                         # Unit tests
│   ├── __init__.py
│   └── test_metrics.py
│
├── logs/                          # Log files (auto-created)
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
├── .env                           # Environment variables template
├── .gitignore                     # Git ignore rules
└── dev_pulse.db                   # SQLite database (auto-created)
```

## Logging System

### Log File Structure

Logs are stored in the `logs/` directory with daily rotation:

```
logs/
├── 27-03-2026.log
├── 28-03-2026.log
└── 29-03-2026.log
```

### Log Format

```
[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE
```

**Example:**
```
[2026-03-27 14:22:01] [INFO] [dev_pulse.services.github_client] - Fetching https://api.github.com/repos/octocat/Hello-World/commits
[2026-03-27 14:22:02] [INFO] [dev_pulse.services.cache_service] - Cache HIT for /repos/octocat/Hello-World/commits
[2026-03-27 14:22:03] [WARNING] [dev_pulse.services.github_client] - Rate limit low: 95 requests remaining
[2026-03-27 14:22:04] [ERROR] [dev_pulse.services.github_client] - API request failed: 404 Not Found
[2026-03-27 14:22:05] [CRITICAL] [dev_pulse.cli.main] - Analysis failed: Connection timeout
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed internal information (optional) |
| INFO | API requests, cache hits/misses, analysis progress |
| WARNING | Rate limit warnings, pagination limits |
| ERROR | API failures, data fetch errors |
| CRITICAL | System failures, unexpected crashes |

## Error Handling

### Common Errors and Solutions

#### GitHub Token Not Configured

**Error Message:**
```
Error: GitHub token not configured. Set GITHUB_TOKEN in .env
```

**Solution:**
Create a `.env` file with your GitHub token:
```
GITHUB_TOKEN=your_github_token_here
```

#### Repository Not Found (404)

**Error Message:**
```
API request failed: 404 Client Error: Not Found for url: https://api.github.com/repos/owner/repo
```

**Solution:**
Verify the repository exists and is spelled correctly (format: `owner/repo`).

#### Rate Limit Exceeded

**Warning Message:**
```
Rate limit low: 10 requests remaining
```

**Solution:**
- Wait for the rate limit to reset
- Use a GitHub token with higher rate limits
- Clear cache to reduce API calls

#### Network Timeout

**Error Message:**
```
Timeout fetching https://api.github.com/repos/owner/repo/commits
```

**Solution:**
- Check your internet connection
- Increase timeout values in configuration
- Retry the command

### Graceful Error Handling

The tool handles errors gracefully by:
- Logging detailed error information
- Returning empty results instead of crashing
- Displaying user-friendly error messages
- Continuing with remaining data when possible

## Performance Considerations

### Rate Limiting

- **Authenticated requests**: 5,000 requests per hour
- **Unauthenticated requests**: 60 requests per hour
- The tool automatically adds delays between requests to avoid hitting limits

### Caching Strategy

- API responses are cached for 24 hours by default
- Subsequent analyses of the same repository will use cached data
- Cache can be cleared manually or expires automatically

### Optimization Tips

1. **Use date filters** to reduce data volume:
   ```bash
   python -m dev_pulse.main analyze --repo owner/repo --since 2024-01-01
   ```

2. **Limit PR analysis** for large repositories:
   ```bash
   python -m dev_pulse.main analyze --repo owner/repo --max-prs 30
   ```

3. **Use user filters** to focus on specific developers:
   ```bash
   python -m dev_pulse.main analyze --repo owner/repo --user username
   ```

4. **Clear cache periodically** to free up disk space:
   ```bash
   python -m dev_pulse.main clear-cache
   ```

## Testing

Dev-Pulse includes a comprehensive test suite to ensure reliability and correctness. The tests cover the core functionality including metrics aggregation, error handling, and edge cases.

### Test Coverage

The test suite includes:
- **Unit tests** for the metrics service
- **Mocked API calls** to avoid hitting GitHub's rate limits
- **Edge case testing** (empty results, error conditions)
- **User filtering** tests
- **PR and review metrics** tests
- **Summary statistics** validation

### Running Tests

#### Prerequisites

Install testing dependencies:

```bash
pip install pytest pytest-cov
```

#### Basic Test Commands

**Run all tests:**
```bash
pytest tests/
```

**Run tests with verbose output:**
```bash
pytest tests/ -v
```

**Run a specific test file:**
```bash
pytest tests/test_metrics.py
```

**Run a specific test function:**
```bash
pytest tests/test_metrics.py::TestMetricsService::test_analyze_activity_basic
```

**Run tests with detailed output and stop on first failure:**
```bash
pytest tests/ -v -x
```

#### Test Coverage Reports

**Generate coverage report in terminal:**
```bash
pytest tests/ --cov=dev_pulse
```

**Generate HTML coverage report:**
```bash
pytest tests/ --cov=dev_pulse --cov-report=html
```

This creates an `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view the coverage report.

**Generate coverage report with missing lines highlighted:**
```bash
pytest tests/ --cov=dev_pulse --cov-report=term-missing
```

#### Running Tests with Custom Python Path

If you encounter module import issues, run tests with PYTHONPATH:

```bash
PYTHONPATH=. pytest tests/
```

Or from the project root:

```bash
python -m pytest tests/
```

### Test Output Example

```
============================= test session starts ==============================
platform darwin -- Python 3.9.0, pytest-7.4.0, pluggy-1.0.0
rootdir: /path/to/dev-pulse
plugins: cov-4.1.0
collected 7 items

tests/test_metrics.py .......                                            [100%]

=============== 7 passed, 0 warnings in 0.25s ================================
```

### Coverage Report Example

```
Name                               Stmts   Miss  Cover
------------------------------------------------------
dev_pulse/__init__.py                  1      0   100%
dev_pulse/cli/__init__.py              0      0   100%
dev_pulse/cli/main.py                 85     85     0%
dev_pulse/core/__init__.py             0      0   100%
dev_pulse/core/config.py              26      3    88%
dev_pulse/core/logger.py              29      2    93%
dev_pulse/db/__init__.py               0      0   100%
dev_pulse/db/database.py              32     22    31%
dev_pulse/db/models.py                21      4    81%
dev_pulse/services/__init__.py         0      0   100%
dev_pulse/services/cache_service.py   43     15    65%
dev_pulse/services/github_client.py   88     88     0%
dev_pulse/services/metrics_service.py 42      0   100%
dev_pulse/utils/__init__.py            0      0   100%
dev_pulse/utils/helpers.py            22      4    82%
dev_pulse/utils/rate_limiter.py       23     18    22%
------------------------------------------------------
TOTAL                                412    241    42%
```

### Writing New Tests

When adding new features, follow the existing test patterns:

```python
import unittest
from unittest.mock import Mock, patch
from dev_pulse.services.metrics_service import MetricsService

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.service = MetricsService()
    
    def test_new_feature_basic(self):
        """Test basic functionality."""
        # Mock dependencies
        with patch('dev_pulse.services.metrics_service.github_client') as mock_github:
            # Set up mock returns
            mock_github.get_commits.return_value = []
            
            # Execute test
            result = self.service.new_method()
            
            # Assert results
            self.assertEqual(result, expected_value)
    
    def test_new_feature_edge_case(self):
        """Test edge case handling."""
        # Test empty inputs, error conditions, etc.
        pass
```

### Continuous Integration

For CI/CD pipelines (GitHub Actions, GitLab CI, etc.), use:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest tests/ --cov=dev_pulse
```

### Troubleshooting Tests

#### Common Test Issues

**Issue: ModuleNotFoundError**
```bash
# Solution: Set PYTHONPATH or run from project root
PYTHONPATH=. pytest tests/
```

**Issue: Tests failing due to rate limits**
```bash
# Solution: Use mocks to avoid real API calls
# Ensure all network calls are mocked in tests
```

**Issue: SQLite database locked**
```bash
# Solution: Close database connections or use in-memory DB for tests
# Add cleanup in tearDown methods
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/gupta-vasu-nand/dev-pulse.git
cd dev-pulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Code Style

The project follows PEP 8 guidelines. Format code using Black:

```bash
# Format all Python files
black dev_pulse/ tests/

# Check code style with flake8
flake8 dev_pulse/ tests/
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=dev_pulse --cov-report=html

# Run specific test file
pytest tests/test_metrics.py -v
```

### Debugging

Enable debug logging for detailed output:

```bash
# Set LOG_LEVEL=DEBUG in .env file
LOG_LEVEL=DEBUG
```

Or run with debug logging:

```bash
# Temporarily enable debug logging
LOG_LEVEL=DEBUG python -m dev_pulse.main analyze --repo owner/repo
```

### Building and Packaging

To build a distributable package:

```bash
# Install build tools
pip install build

# Build package
python -m build

# Install locally for testing
pip install -e .
```

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Ensure all tests pass** before submitting
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

### Release Process

1. Update version in `dev_pulse/__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
5. Push tags: `git push --tags`
6. Build and publish to PyPI (if applicable)

## License

MIT License

Copyright (c) 2026 Dev-Pulse Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- GitHub REST API for providing the data
- Click framework for CLI interface
- Rich library for beautiful terminal output
- All contributors and users of this tool
