"""Configuration management for Dev-Pulse."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Load .env file if exists
        env_file = Path(__file__).parent.parent.parent / '.env'
        if env_file.exists():
            load_dotenv(env_file)
        
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.github_api_base = 'https://api.github.com'
        
        # Cache settings
        self.cache_ttl_hours = int(os.getenv('CACHE_TTL_HOURS', '24'))
        self.db_path = Path(os.getenv('DB_PATH', 'dev_pulse.db'))
        
        # Logging settings
        self.log_dir = Path(os.getenv('LOG_DIR', 'logs'))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Rate limiting
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '1'))
        
        # Ensure directories exist
        self.log_dir.mkdir(exist_ok=True)
        self.db_path.parent.mkdir(exist_ok=True)
    
    def validate_token(self) -> bool:
        """Validate GitHub token."""
        return bool(self.github_token and len(self.github_token) > 10)


config = Config()