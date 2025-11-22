"""
Unit tests for configuration modules.
"""
import pytest
import os
from src.config.settings import DatabaseConfig, AppConfig, EnvironmentConfig, PathConfig
from src.config.constants import (
    MIN_QUANTITY, MIN_UNIT_PRICE, CSV_ENCODING,
    CUSTOMER_SEGMENTS, COLOR_SCHEMES, ERROR_MESSAGES
)


@pytest.mark.unit
class TestDatabaseConfig:
    """Test cases for DatabaseConfig class."""

    def test_database_config_defaults(self, mock_env_vars):
        """Test database configuration with environment variables."""
        assert DatabaseConfig.DB_NAME == 'test_db'
        assert DatabaseConfig.DB_USER == 'test_user'
        assert DatabaseConfig.DB_PASSWORD == 'test_password'
        assert DatabaseConfig.DB_HOST == 'localhost'
        assert DatabaseConfig.DB_PORT == 5432

    def test_connection_string(self, mock_env_vars):
        """Test database connection string generation."""
        conn_str = DatabaseConfig.get_connection_string()
        expected = "postgresql://test_user:test_password@localhost:5432/test_db"
        assert conn_str == expected

    def test_validation_success(self, mock_env_vars):
        """Test successful configuration validation."""
        assert DatabaseConfig.validate() is True

    def test_validation_failure(self, monkeypatch):
        """Test configuration validation with missing values."""
        monkeypatch.setenv('DB_NAME', '')
        monkeypatch.setenv('DB_USER', 'user')
        monkeypatch.setenv('DB_PASSWORD', 'pass')

        with pytest.raises(ValueError, match="Missing required database configuration"):
            DatabaseConfig.validate()


@pytest.mark.unit
class TestAppConfig:
    """Test cases for AppConfig class."""

    def test_app_config_defaults(self):
        """Test application configuration defaults."""
        assert AppConfig.PAGE_TITLE == "Sales Analytics Dashboard"
        assert AppConfig.LAYOUT == "wide"
        assert AppConfig.CACHE_TTL == 600
        assert AppConfig.CHART_HEIGHT == 400

    def test_app_config_limits(self):
        """Test display limit configurations."""
        assert AppConfig.TOP_PRODUCTS_LIMIT == 10
        assert AppConfig.TOP_CUSTOMERS_LIMIT == 10
        assert AppConfig.TOP_COUNTRIES_LIMIT == 10

    def test_app_config_formatting(self):
        """Test formatting configurations."""
        assert AppConfig.CURRENCY_SYMBOL == "$"
        assert AppConfig.DECIMAL_PLACES == 2
        assert AppConfig.THOUSAND_SEPARATOR == ","


@pytest.mark.unit
class TestEnvironmentConfig:
    """Test cases for EnvironmentConfig class."""

    def test_environment_config(self, mock_env_vars):
        """Test environment configuration."""
        assert EnvironmentConfig.ENV == 'testing'
        assert EnvironmentConfig.DEBUG is True
        assert EnvironmentConfig.LOG_LEVEL == 'DEBUG'

    def test_is_production(self, monkeypatch):
        """Test production environment detection."""
        monkeypatch.setenv('ENVIRONMENT', 'production')
        # Need to reload the module for changes to take effect
        assert EnvironmentConfig.ENV == 'production'

    def test_is_development(self, mock_env_vars):
        """Test development environment detection."""
        # mock_env_vars sets ENVIRONMENT to 'testing'
        assert not EnvironmentConfig.is_development()


@pytest.mark.unit
class TestPathConfig:
    """Test cases for PathConfig class."""

    def test_path_config_structure(self):
        """Test path configuration structure."""
        assert PathConfig.PROJECT_ROOT is not None
        assert PathConfig.DATA_DIR is not None
        assert PathConfig.LOG_DIR is not None

    def test_ensure_directories_creates_paths(self, tmp_path, monkeypatch):
        """Test that ensure_directories creates required paths."""
        # Mock PROJECT_ROOT to use tmp_path
        monkeypatch.setattr(PathConfig, 'PROJECT_ROOT', str(tmp_path))
        monkeypatch.setattr(PathConfig, 'DATA_DIR', str(tmp_path / 'data'))
        monkeypatch.setattr(PathConfig, 'RAW_DATA_DIR', str(tmp_path / 'data' / 'raw'))
        monkeypatch.setattr(PathConfig, 'LOG_DIR', str(tmp_path / 'logs'))

        PathConfig.ensure_directories()

        assert os.path.exists(tmp_path / 'data' / 'raw')
        assert os.path.exists(tmp_path / 'logs')


@pytest.mark.unit
class TestConstants:
    """Test cases for constants module."""

    def test_data_validation_constants(self):
        """Test data validation constants."""
        assert MIN_QUANTITY == 1
        assert MIN_UNIT_PRICE == 0.01

    def test_csv_constants(self):
        """Test CSV-related constants."""
        assert CSV_ENCODING == 'ISO-8859-1'

    def test_customer_segments_structure(self):
        """Test customer segments structure."""
        assert 'Champions' in CUSTOMER_SEGMENTS
        assert 'description' in CUSTOMER_SEGMENTS['Champions']
        assert 'rfm_threshold' in CUSTOMER_SEGMENTS['Champions']
        assert 'color' in CUSTOMER_SEGMENTS['Champions']

    def test_color_schemes_structure(self):
        """Test color schemes structure."""
        assert 'primary' in COLOR_SCHEMES
        assert 'categorical' in COLOR_SCHEMES
        assert isinstance(COLOR_SCHEMES['categorical'], list)

    def test_error_messages_structure(self):
        """Test error messages structure."""
        assert 'database_connection' in ERROR_MESSAGES
        assert 'no_data' in ERROR_MESSAGES
        assert 'query_failed' in ERROR_MESSAGES
        assert isinstance(ERROR_MESSAGES['query_failed'], str)
