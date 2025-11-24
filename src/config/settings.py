"""
Application settings and configuration management.

This module provides centralized configuration for the sales analytics dashboard,
including database settings, application settings, and environment-specific configurations.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Database connection configuration."""

    DB_NAME: str = os.getenv('DB_NAME', 'sales_analytics')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))

    @classmethod
    def get_connection_string(cls) -> str:
        """
        Get PostgreSQL connection string.

        Returns:
            str: Database connection string
        """
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def validate(cls) -> bool:
        """
        Validate database configuration.

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If required configuration is missing
        """
        if not cls.DB_NAME or not cls.DB_USER or not cls.DB_PASSWORD:
            raise ValueError("Missing required database configuration. Check your .env file.")
        return True


class AppConfig:
    """Application configuration."""

    # Page settings
    PAGE_TITLE: str = "Sales Analytics Dashboard"
    PAGE_ICON: str = "📊"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"

    # Cache settings
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '600'))  # 10 minutes default

    # Data refresh settings
    AUTO_REFRESH: bool = os.getenv('AUTO_REFRESH', 'false').lower() == 'true'
    REFRESH_INTERVAL: int = int(os.getenv('REFRESH_INTERVAL', '300'))  # 5 minutes default

    # Display settings
    CHART_HEIGHT: int = 400
    TOP_PRODUCTS_LIMIT: int = 10
    TOP_CUSTOMERS_LIMIT: int = 10
    TOP_COUNTRIES_LIMIT: int = 10

    # Number formatting
    CURRENCY_SYMBOL: str = "$"
    DECIMAL_PLACES: int = 2
    THOUSAND_SEPARATOR: str = ","


class EnvironmentConfig:
    """Environment-specific configuration."""

    ENV: str = os.getenv('ENVIRONMENT', 'development')
    DEBUG: bool = os.getenv('DEBUG', 'true').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENV.lower() == 'production'

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.ENV.lower() == 'development'


class APIConfig:
    """API configuration for FastAPI application."""

    # API Server settings
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))

    # JWT Authentication settings
    SECRET_KEY: str = os.getenv('API_SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

    # API Documentation
    API_TITLE: str = "Sales Analytics API"
    API_DESCRIPTION: str = "Professional REST API for sales analytics with secure authentication"
    API_VERSION: str = "1.0.0"

    @classmethod
    def validate(cls) -> bool:
        """
        Validate API configuration.

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If SECRET_KEY is not set properly in production
        """
        if EnvironmentConfig.is_production() and cls.SECRET_KEY == 'your-secret-key-change-in-production':
            raise ValueError("API_SECRET_KEY must be set in production. Generate with: openssl rand -hex 32")
        return True


class EmailConfig:
    """Email configuration for sending verification emails via SendGrid."""

    # Email service enabled
    EMAIL_ENABLED: bool = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'

    # SendGrid API Key
    SENDGRID_API_KEY: str = os.getenv('SENDGRID_API_KEY', '')

    # Email sender details
    EMAIL_FROM: str = os.getenv('EMAIL_FROM', 'noreply@salesanalytics.com')
    EMAIL_FROM_NAME: str = os.getenv('EMAIL_FROM_NAME', 'Sales Analytics')

    # Email verification URL
    EMAIL_VERIFICATION_URL: str = os.getenv('EMAIL_VERIFICATION_URL', 'http://localhost:8000/api/auth/verify-email')

    @classmethod
    def validate(cls) -> bool:
        """
        Validate email configuration.

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If email is enabled but SENDGRID_API_KEY is missing
        """
        if cls.EMAIL_ENABLED and not cls.SENDGRID_API_KEY:
            raise ValueError(
                "Email enabled but SENDGRID_API_KEY not configured. "
                "Get your API key from: https://app.sendgrid.com/settings/api_keys"
            )
        return True


class PathConfig:
    """Path configuration for project directories."""

    # Get project root directory
    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Data directories
    DATA_DIR: str = os.path.join(PROJECT_ROOT, 'data')
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, 'raw')

    # Log directory
    LOG_DIR: str = os.path.join(PROJECT_ROOT, 'logs')

    # Default data file
    DEFAULT_CSV_FILE: str = os.path.join(RAW_DATA_DIR, 'data.csv')

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.LOG_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Initialize and validate configuration on import
# Make validation optional to support Streamlit Cloud deployment
try:
    PathConfig.ensure_directories()
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

# Only validate database config if not in Streamlit Cloud or if credentials are provided
if os.getenv('DB_PASSWORD'):
    try:
        DatabaseConfig.validate()
    except ValueError as e:
        print(f"Configuration Warning: {e}")
        print("Database credentials must be configured in Streamlit Cloud secrets.")
