"""
Unit tests for ETL transform module.
"""
import pytest
import pandas as pd
from src.etl.transform import clean_sales_data


@pytest.mark.unit
@pytest.mark.etl
class TestCleanSalesData:
    """Test cases for clean_sales_data function."""

    def test_clean_removes_cancelled_orders(self, sample_raw_data):
        """Test that cancelled orders (starting with 'C') are removed."""
        df_clean = clean_sales_data(sample_raw_data.copy())

        # Original has 1 cancelled order (C536368)
        cancelled_orders = sample_raw_data[
            sample_raw_data['InvoiceNo'].astype(str).str.startswith('C')
        ]
        assert len(cancelled_orders) == 1

        # Cleaned data should not have cancelled orders
        assert not any(df_clean['InvoiceNo'].astype(str).str.startswith('C'))

    def test_clean_removes_negative_quantities(self, sample_raw_data):
        """Test that negative quantities are removed."""
        df_clean = clean_sales_data(sample_raw_data.copy())

        # All quantities should be positive
        assert all(df_clean['Quantity'] > 0)

    def test_clean_removes_zero_prices(self, sample_raw_data):
        """Test that zero or negative prices are removed."""
        df_clean = clean_sales_data(sample_raw_data.copy())

        # All prices should be positive
        assert all(df_clean['UnitPrice'] > 0)

    def test_clean_calculates_total_amount(self, sample_raw_data):
        """Test that TotalAmount is calculated correctly."""
        df_clean = clean_sales_data(sample_raw_data.copy())

        # TotalAmount should exist
        assert 'TotalAmount' in df_clean.columns

        # Verify calculation
        for idx, row in df_clean.iterrows():
            expected_total = row['Quantity'] * row['UnitPrice']
            assert row['TotalAmount'] == pytest.approx(expected_total)

    def test_clean_converts_invoice_date(self, sample_raw_data):
        """Test that InvoiceDate is converted to datetime."""
        df_clean = clean_sales_data(sample_raw_data.copy())

        # InvoiceDate should be datetime type
        assert pd.api.types.is_datetime64_any_dtype(df_clean['InvoiceDate'])

    def test_clean_preserves_valid_data(self):
        """Test that valid data is preserved."""
        valid_data = pd.DataFrame({
            'InvoiceNo': ['536365', '536366'],
            'StockCode': ['85123A', '71053'],
            'Description': ['PRODUCT A', 'PRODUCT B'],
            'Quantity': [6, 10],
            'InvoiceDate': ['2010-12-01 08:26:00', '2010-12-01 08:28:00'],
            'UnitPrice': [2.55, 3.39],
            'CustomerID': [17850.0, 17850.0],
            'Country': ['United Kingdom', 'United Kingdom']
        })

        df_clean = clean_sales_data(valid_data.copy())

        # Should preserve both rows
        assert len(df_clean) == 2

    def test_clean_returns_dataframe(self, sample_raw_data):
        """Test that function returns a DataFrame."""
        result = clean_sales_data(sample_raw_data.copy())
        assert isinstance(result, pd.DataFrame)

    def test_clean_empty_dataframe(self):
        """Test cleaning an empty DataFrame."""
        empty_df = pd.DataFrame(columns=[
            'InvoiceNo', 'StockCode', 'Description', 'Quantity',
            'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country'
        ])

        df_clean = clean_sales_data(empty_df.copy())
        assert len(df_clean) == 0
        assert 'TotalAmount' in df_clean.columns

    def test_clean_combined_filters(self, sample_raw_data):
        """Test that all cleaning steps work together."""
        df_clean = clean_sales_data(sample_raw_data.copy())

        # Original has 5 rows
        assert len(sample_raw_data) == 5

        # After cleaning:
        # - Remove 1 cancelled order (C536368)
        # - Remove 1 negative quantity (536367)
        # - Remove 1 zero price (536367 also has zero price)
        # Should have 3 valid rows
        assert len(df_clean) == 3
