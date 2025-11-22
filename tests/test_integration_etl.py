"""
Integration tests for ETL pipeline.
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.etl.extract import extract_csv
from src.etl.transform import clean_sales_data
from src.etl.load import load_to_database


@pytest.mark.integration
@pytest.mark.etl
class TestETLPipeline:
    """Integration tests for complete ETL pipeline."""

    def test_full_etl_pipeline(self, temp_csv_file):
        """Test complete ETL pipeline flow."""
        # Extract
        df_raw = extract_csv(temp_csv_file)
        assert len(df_raw) == 5

        # Transform
        df_clean = clean_sales_data(df_raw)
        assert len(df_clean) == 3  # After cleaning
        assert 'TotalAmount' in df_clean.columns
        assert all(df_clean['Quantity'] > 0)
        assert all(df_clean['UnitPrice'] > 0)

        # Load (mocked)
        with patch('src.etl.load.get_connection') as mock_get_conn:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_get_conn.return_value = mock_conn

            rows_inserted = load_to_database(df_clean)

            assert rows_inserted == 3
            mock_conn.commit.assert_called_once()

    def test_etl_data_integrity(self, temp_csv_file):
        """Test that data integrity is maintained through ETL."""
        # Extract
        df_raw = extract_csv(temp_csv_file)

        # Transform
        df_clean = clean_sales_data(df_raw)

        # Verify data types
        assert pd.api.types.is_datetime64_any_dtype(df_clean['InvoiceDate'])
        assert pd.api.types.is_numeric_dtype(df_clean['Quantity'])
        assert pd.api.types.is_numeric_dtype(df_clean['UnitPrice'])
        assert pd.api.types.is_numeric_dtype(df_clean['TotalAmount'])

        # Verify calculations
        for idx, row in df_clean.iterrows():
            expected_total = row['Quantity'] * row['UnitPrice']
            assert row['TotalAmount'] == pytest.approx(expected_total)

    def test_etl_with_real_csv_data(self, tmp_path):
        """Test ETL pipeline with realistic CSV data."""
        # Create realistic test data
        data = pd.DataFrame({
            'InvoiceNo': ['536365', '536366', 'C536367', '536368', '536369'],
            'StockCode': ['85123A', '71053', '84406B', '84029G', '84029E'],
            'Description': ['WHITE HANGING HEART', 'WHITE METAL LANTERN',
                          'CREAM CUPID HEARTS', 'KNITTED UNION FLAG',
                          'RED WOOLLY HOTTIE'],
            'Quantity': [6, 10, -5, 12, 8],
            'InvoiceDate': [
                '2010-12-01 08:26:00',
                '2010-12-01 08:28:00',
                '2010-12-01 08:34:00',
                '2010-12-01 08:35:00',
                '2010-12-01 08:45:00'
            ],
            'UnitPrice': [2.55, 3.39, 0.00, 4.25, 5.75],
            'CustomerID': [17850.0, 17850.0, 13047.0, 13047.0, 13047.0],
            'Country': ['United Kingdom', 'United Kingdom', 'France', 'France', 'France']
        })

        csv_path = tmp_path / "realistic_data.csv"
        data.to_csv(csv_path, index=False)

        # Run ETL
        df_raw = extract_csv(str(csv_path))
        df_clean = clean_sales_data(df_raw)

        # Validate results
        # After cleaning: removed 1 cancelled order (C536367), kept the rest (4 records)
        assert len(df_clean) == 4  # Only valid records excluding cancelled
        assert all(df_clean['InvoiceNo'].isin(['536365', '536366', '536368', '536369']))
        assert all(df_clean['Quantity'] > 0)
        assert all(df_clean['UnitPrice'] > 0)

    @patch('src.etl.load.get_connection')
    def test_etl_error_handling(self, mock_get_conn, temp_csv_file):
        """Test ETL pipeline error handling."""
        # Extract
        df_raw = extract_csv(temp_csv_file)

        # Transform
        df_clean = clean_sales_data(df_raw)

        # Load with simulated error
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        mock_cursor.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            load_to_database(df_clean)

        # Verify rollback was called
        mock_conn.rollback.assert_called_once()

    def test_etl_preserves_data_quality(self, temp_csv_file):
        """Test that ETL maintains data quality standards."""
        df_raw = extract_csv(temp_csv_file)
        df_clean = clean_sales_data(df_raw)

        # No cancelled orders
        assert not any(df_clean['InvoiceNo'].astype(str).str.startswith('C'))

        # All positive quantities
        assert all(df_clean['Quantity'] >= 1)

        # All positive prices
        assert all(df_clean['UnitPrice'] >= 0.01)

        # All total amounts calculated correctly
        for idx, row in df_clean.iterrows():
            assert row['TotalAmount'] == row['Quantity'] * row['UnitPrice']

        # Valid date format
        assert pd.api.types.is_datetime64_any_dtype(df_clean['InvoiceDate'])
