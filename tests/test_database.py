"""
Unit tests for database connection module.
"""
import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from src.database.connection import get_connection


@pytest.mark.unit
@pytest.mark.database
class TestDatabaseConnection:
    """Test cases for database connection."""

    @patch('src.database.connection.psycopg2.connect')
    def test_get_connection_success(self, mock_connect, mock_env_vars):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_connection()

        assert conn == mock_conn
        mock_connect.assert_called_once_with(
            dbname='test_db',
            user='test_user',
            password='test_password',
            host='localhost',
            port=5432
        )

    @patch('src.database.connection.psycopg2.connect')
    def test_get_connection_failure(self, mock_connect, mock_env_vars):
        """Test database connection failure."""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        with pytest.raises(psycopg2.Error, match="Connection failed"):
            get_connection()

    @patch('src.database.connection.psycopg2.connect')
    def test_get_connection_uses_config(self, mock_connect, mock_env_vars):
        """Test that connection uses DatabaseConfig values."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        get_connection()

        # Verify connection parameters from config
        call_kwargs = mock_connect.call_args[1]
        assert call_kwargs['dbname'] == 'test_db'
        assert call_kwargs['user'] == 'test_user'
        assert call_kwargs['host'] == 'localhost'
        assert call_kwargs['port'] == 5432
