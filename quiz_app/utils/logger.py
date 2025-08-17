"""Logging utilities for the application."""
import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """Custom logger class for the quiz application."""
    
    def __init__(self, name: str, log_file: Optional[str] = None, level: str = 'INFO'):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_file: Log file path
            level: Log level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Avoid adding duplicate handlers
        if not self.logger.handlers:
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # File handler if log_file provided
            if log_file:
                try:
                    # Create directory if it doesn't exist
                    log_dir = os.path.dirname(log_file)
                    if log_dir and not os.path.exists(log_dir):
                        os.makedirs(log_dir, exist_ok=True)
                    
                    file_handler = logging.FileHandler(log_file, encoding='utf-8')
                    file_handler.setFormatter(formatter)
                    self.logger.addHandler(file_handler)
                except Exception as e:
                    # If file logging fails, just use console logging
                    print(f"Warning: Could not create log file {log_file}: {e}")
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def exception(self, message: str) -> None:
        """Log exception with traceback."""
        self.logger.exception(message)