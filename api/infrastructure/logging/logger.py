import logging
import sys
from typing import Optional
from pathlib import Path

from api.settings.app_settings import settings


class AppLogger:
    """Centralized logging configuration for the application."""
    
    _instance: Optional['AppLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self) -> None:
        """Configure logging based on environment settings."""
        # Get log level from environment or use INFO as default
        log_level = getattr(logging, 
                           getattr(settings, 'log_level', 'INFO').upper(), 
                           logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if configured)
        log_file = getattr(settings, 'log_file', None)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Set specific logger levels for third-party libraries
        logging.getLogger('boto3').setLevel(logging.WARNING)
        logging.getLogger('botocore').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for the given name."""
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger instance."""
    app_logger = AppLogger()
    return app_logger.get_logger(name)


# Initialize logging when module is imported
_app_logger = AppLogger()