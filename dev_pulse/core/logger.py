"""Centralized logging system for Dev-Pulse."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import threading


class SingletonLogger:
    """Singleton logger instance with file and console handlers."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Create singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize logger with handlers."""
        from dev_pulse.core.config import config
        
        self.logger = logging.getLogger('DevPulse')
        self.logger.setLevel(getattr(logging, config.log_level))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        log_file = config.log_dir / f"{datetime.now().strftime('%d-%m-%Y')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """Return the logger instance."""
        return self.logger


class ModuleLogger:
    """Wrapper for module-specific logging."""
    
    def __init__(self, module_name: str):
        """Initialize module logger."""
        self.logger = SingletonLogger().get_logger()
        self.module_name = module_name
    
    def _log(self, level: int, msg: str, *args, **kwargs):
        """Log with module prefix."""
        formatted_msg = f"[{self.module_name}] {msg}"
        self.logger.log(level, formatted_msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log info message."""
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, msg, *args, **kwargs)


def get_logger(module_name: str = None):
    """Get logger instance for a module."""
    if module_name:
        return ModuleLogger(module_name)
    return SingletonLogger().get_logger()