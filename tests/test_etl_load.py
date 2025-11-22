"""
Unit tests for ETL load module.
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.etl.load import load_to_database


@pytest.mark.unit
@pytest.mark.etl
@pytest.mark.database
class TestLoadToDatabase:
    """Test cases for load_to_database function."""

    @patch('src.etl.load.get_connection')
    def test_load_success(self, mock_get_conn, sample_clean_data):
        """Test successful database loading."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        rows_inserted = load_to_database(sample_clean_data)

        # Verify rows inserted
        assert rows_inserted == len(sample_clean_data)

        # Verify cursor execute was called for each row
        assert mock_cursor.execute.call_count == len(sample_clean_data)

        # Verify commit was called
        mock_conn.commit.assert_called_once()

        # Verify connection was closed
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.etl.load.get_connection')
    def test_load_handles_none_customer_id(self, mock_get_conn):
        """Test loading with None CustomerID values."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        data_with_none = pd.DataFrame({
            'InvoiceNo': ['536365'],
            'StockCode': ['85123A'],
            'Description': ['PRODUCT A'],
            'Quantity': [6],
            'InvoiceDate': pd.to_datetime(['2010-12-01 08:26:00']),
            'UnitPrice': [2.55],
            'CustomerID': [None],
            'Country': ['United Kingdom'],
            'TotalAmount': [15.30]
        })

        rows_inserted = load_to_database(data_with_none)
        assert rows_inserted == 1

    @patch('src.etl.load.get_connection')
    def test_load_handles_unknown_description(self, mock_get_conn):
        """Test loading with None Description values."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        data_with_none_desc = pd.DataFrame({
            'InvoiceNo': ['536365'],
            'StockCode': ['85123A'],
            'Description': [None],
            'Quantity': [6],
            'InvoiceDate': pd.to_datetime(['2010-12-01 08:26:00']),
            'UnitPrice': [2.55],
            'CustomerID': [17850.0],
            'Country': ['United Kingdom'],
            'TotalAmount': [15.30]
        })

        load_to_database(data_with_none_desc)

        # Verify 'Unknown' was used for None description
        call_args = mock_cursor.execute.call_args[0][1]
        assert call_args[2] == 'Unknown'

    @patch('src.etl.load.get_connection')
    def test_load_rollback_on_error(self, mock_get_conn, sample_clean_data):
        """Test that database is rolled back on error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Simulate database error
        mock_cursor.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            load_to_database(sample_clean_data)

        # Verify rollback was called
        mock_conn.rollback.assert_called_once()

    @patch('src.etl.load.get_connection')
    def test_load_closes_connection_on_error(self, mock_get_conn, sample_clean_data):
        """Test that connection is closed even on error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Simulate database error
        mock_cursor.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception):
            load_to_database(sample_clean_data)

        # Verify connection was still closed
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.etl.load.get_connection')
    def test_load_empty_dataframe(self, mock_get_conn):
        """Test loading an empty DataFrame."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        empty_df = pd.DataFrame(columns=[
            'InvoiceNo', 'StockCode', 'Description', 'Quantity',
            'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country', 'TotalAmount'
        ])

        rows_inserted = load_to_database(empty_df)

        assert rows_inserted == 0
        mock_cursor.execute.assert_not_called()
        mock_conn.commit.assert_called_once()

    @patch('src.etl.load.get_connection')
    def test_load_batch_logging(self, mock_get_conn):
        """Test that batch progress is logged at correct intervals."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        # Create data with 2500 rows (should log at 1000, 2000)
        large_data = pd.DataFrame({
            'InvoiceNo': [f'{i}' for i in range(2500)],
            'StockCode': ['ABC'] * 2500,
            'Description': ['Product'] * 2500,
            'Quantity': [1] * 2500,
            'InvoiceDate': pd.to_datetime(['2010-12-01'] * 2500),
            'UnitPrice': [10.0] * 2500,
            'CustomerID': [100.0] * 2500,
            'Country': ['UK'] * 2500,
            'TotalAmount': [10.0] * 2500
        })

        rows_inserted = load_to_database(large_data)
        assert rows_inserted == 2500
