"""
Pytest configuration and shared fixtures.
"""
import pytest
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_raw_data():
    """Create sample raw sales data for testing."""
    return pd.DataFrame({
        'InvoiceNo': ['536365', '536366', '536367', 'C536368', '536369'],
        'StockCode': ['85123A', '71053', '84406B', '84029G', '84029E'],
        'Description': ['PRODUCT A', 'PRODUCT B', 'PRODUCT C', 'PRODUCT D', 'PRODUCT E'],
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


@pytest.fixture
def sample_clean_data():
    """Create sample cleaned sales data for testing."""
    data = pd.DataFrame({
        'InvoiceNo': ['536365', '536366', '536369'],
        'StockCode': ['85123A', '71053', '84029E'],
        'Description': ['PRODUCT A', 'PRODUCT B', 'PRODUCT E'],
        'Quantity': [6, 10, 8],
        'InvoiceDate': pd.to_datetime([
            '2010-12-01 08:26:00',
            '2010-12-01 08:28:00',
            '2010-12-01 08:45:00'
        ]),
        'UnitPrice': [2.55, 3.39, 5.75],
        'CustomerID': [17850.0, 17850.0, 13047.0],
        'Country': ['United Kingdom', 'United Kingdom', 'France']
    })
    data['TotalAmount'] = data['Quantity'] * data['UnitPrice']
    return data


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def sample_kpi_data():
    """Sample KPI data for testing."""
    return {
        'revenue': 1000000.0,
        'orders': 5000,
        'customers': 1000,
        'avg_order': 200.0
    }


@pytest.fixture
def sample_revenue_trend():
    """Sample revenue trend data."""
    dates = pd.date_range(start='2010-12-01', end='2010-12-10', freq='D')
    return pd.DataFrame({
        'date': dates,
        'revenue': [1000 + i * 100 for i in range(len(dates))],
        'orders': [50 + i * 5 for i in range(len(dates))]
    })


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return pd.DataFrame({
        'product': ['Product A', 'Product B', 'Product C'],
        'revenue': [50000, 30000, 20000],
        'units_sold': [500, 300, 200],
        'orders': [100, 80, 60]
    })


@pytest.fixture
def sample_country_data():
    """Sample country performance data."""
    return pd.DataFrame({
        'country': ['United Kingdom', 'France', 'Germany'],
        'revenue': [500000, 300000, 200000],
        'orders': [2000, 1500, 1000],
        'customers': [500, 400, 300]
    })


@pytest.fixture
def sample_customer_segments():
    """Sample customer segmentation data."""
    return pd.DataFrame({
        'segment': ['VIP', 'Regular', 'Low Value'],
        'customers': [100, 500, 400],
        'avg_revenue': [5000, 1000, 200]
    })


@pytest.fixture
def temp_csv_file(tmp_path, sample_raw_data):
    """Create a temporary CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    sample_raw_data.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv('DB_NAME', 'test_db')
    monkeypatch.setenv('DB_USER', 'test_user')
    monkeypatch.setenv('DB_PASSWORD', 'test_password')
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_PORT', '5432')
    monkeypatch.setenv('ENVIRONMENT', 'testing')
    monkeypatch.setenv('DEBUG', 'true')
    monkeypatch.setenv('LOG_LEVEL', 'DEBUG')

    # Force reload of config classes to pick up test env vars
    import importlib
    from src.config import settings
    importlib.reload(settings)
