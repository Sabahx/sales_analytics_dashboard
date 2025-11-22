"""
Unit tests for ETL extract module.
"""
import pytest
import pandas as pd
import os
from src.etl.extract import extract_csv


@pytest.mark.unit
@pytest.mark.etl
class TestExtractCSV:
    """Test cases for extract_csv function."""

    def test_extract_csv_success(self, temp_csv_file):
        """Test successful CSV extraction."""
        df = extract_csv(temp_csv_file)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == [
            'InvoiceNo', 'StockCode', 'Description', 'Quantity',
            'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country'
        ]

    def test_extract_csv_file_not_found(self):
        """Test extraction with non-existent file."""
        with pytest.raises(FileNotFoundError):
            extract_csv('nonexistent_file.csv')

    def test_extract_csv_missing_columns(self, tmp_path):
        """Test extraction with missing required columns."""
        # Create CSV with missing columns
        invalid_data = pd.DataFrame({
            'InvoiceNo': ['123'],
            'StockCode': ['ABC']
        })
        csv_path = tmp_path / "invalid.csv"
        invalid_data.to_csv(csv_path, index=False)

        with pytest.raises(ValueError, match="CSV missing required columns"):
            extract_csv(str(csv_path))

    def test_extract_csv_empty_file(self, tmp_path):
        """Test extraction with empty CSV file."""
        # Create empty CSV with headers only
        empty_data = pd.DataFrame(columns=[
            'InvoiceNo', 'StockCode', 'Description', 'Quantity',
            'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country'
        ])
        csv_path = tmp_path / "empty.csv"
        empty_data.to_csv(csv_path, index=False)

        df = extract_csv(str(csv_path))
        assert len(df) == 0
        assert list(df.columns) == [
            'InvoiceNo', 'StockCode', 'Description', 'Quantity',
            'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country'
        ]

    def test_extract_csv_custom_encoding(self, tmp_path):
        """Test extraction with custom encoding."""
        data = pd.DataFrame({
            'InvoiceNo': ['123'],
            'StockCode': ['ABC'],
            'Description': ['Product'],
            'Quantity': [1],
            'InvoiceDate': ['2010-12-01'],
            'UnitPrice': [10.0],
            'CustomerID': [100],
            'Country': ['UK']
        })
        csv_path = tmp_path / "utf8.csv"
        data.to_csv(csv_path, index=False, encoding='utf-8')

        df = extract_csv(str(csv_path), encoding='utf-8')
        assert len(df) == 1
