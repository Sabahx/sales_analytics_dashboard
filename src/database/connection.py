"""
Database connection management module.
"""
import psycopg2
from src.config.settings import DatabaseConfig
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def get_connection():
    """
    Get PostgreSQL database connection.

    Returns:
        psycopg2.connection: Database connection object

    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        logger.debug("Attempting database connection...")
        conn = psycopg2.connect(
            dbname=DatabaseConfig.DB_NAME,
            user=DatabaseConfig.DB_USER,
            password=DatabaseConfig.DB_PASSWORD,
            host=DatabaseConfig.DB_HOST,
            port=DatabaseConfig.DB_PORT
        )
        logger.debug("Database connection successful")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise
