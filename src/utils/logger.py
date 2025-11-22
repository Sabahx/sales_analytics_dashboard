"""
Logging configuration module.

This module provides centralized logging configuration for the sales analytics dashboard.
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

from src.config.settings import PathConfig, EnvironmentConfig


class LoggerConfig:
    """Logger configuration and setup."""

    # Log format
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    # Log file settings
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5

    @classmethod
    def setup_logger(
        cls,
        name: str = 'sales_analytics',
        log_file: Optional[str] = None,
        level: Optional[str] = None
    ) -> logging.Logger:
        """
        Setup and configure logger.

        Args:
            name (str): Logger name
            log_file (str, optional): Log file path. If None, uses default
            level (str, optional): Log level. If None, uses environment config

        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logger
        logger = logging.getLogger(name)

        # Set log level
        log_level = level or EnvironmentConfig.LOG_LEVEL
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # Create formatter
        formatter = logging.Formatter(cls.LOG_FORMAT, cls.DATE_FORMAT)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_file is None:
            log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            log_file = os.path.join(PathConfig.LOG_DIR, log_filename)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=cls.MAX_BYTES,
            backupCount=cls.BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG if EnvironmentConfig.DEBUG else logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Log initialization
        logger.info(f"Logger '{name}' initialized")
        logger.info(f"Log level: {log_level.upper()}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Environment: {EnvironmentConfig.ENV}")

        return logger

    @classmethod
    def get_logger(cls, name: str = 'sales_analytics') -> logging.Logger:
        """
        Get or create logger instance.

        Args:
            name (str): Logger name

        Returns:
            logging.Logger: Logger instance
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            return cls.setup_logger(name)
        return logger


# Module-level logger for convenience
def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get logger for a specific module.

    Args:
        module_name (str): Module name (usually __name__)

    Returns:
        logging.Logger: Logger instance for the module
    """
    return LoggerConfig.get_logger(module_name)


# Default application logger
app_logger = LoggerConfig.setup_logger('sales_analytics')
