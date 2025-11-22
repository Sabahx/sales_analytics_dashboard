"""
Application constants and business rules.

This module contains constants used throughout the application,
including customer segmentation thresholds, chart configurations, and business logic constants.
"""

# ===========================
# Customer Segmentation
# ===========================

# RFM (Recency, Frequency, Monetary) score thresholds
RFM_SCORE_MIN = 1
RFM_SCORE_MAX = 5

# Customer segment definitions based on RFM scores
CUSTOMER_SEGMENTS = {
    'Champions': {
        'description': 'Recent buyers, frequent purchasers, high spenders',
        'rfm_threshold': {'recency': 4, 'frequency': 4, 'monetary': 4},
        'color': '#1f77b4'
    },
    'Loyal Customers': {
        'description': 'Frequent buyers with good spending',
        'rfm_threshold': {'recency': 3, 'frequency': 4, 'monetary': 3},
        'color': '#ff7f0e'
    },
    'Potential Loyalists': {
        'description': 'Recent customers with average frequency',
        'rfm_threshold': {'recency': 4, 'frequency': 2, 'monetary': 2},
        'color': '#2ca02c'
    },
    'At Risk': {
        'description': 'Good customers who haven\'t purchased recently',
        'rfm_threshold': {'recency': 1, 'frequency': 3, 'monetary': 3},
        'color': '#d62728'
    },
    'Lost': {
        'description': 'Haven\'t purchased in a long time',
        'rfm_threshold': {'recency': 1, 'frequency': 1, 'monetary': 1},
        'color': '#9467bd'
    }
}

# Customer lifetime value thresholds (in currency)
CLV_THRESHOLDS = {
    'high_value': 10000,
    'medium_value': 5000,
    'low_value': 1000
}


# ===========================
# Time-based Constants
# ===========================

# Day of week mapping
DAYS_OF_WEEK = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

# Month names
MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# Business hours
BUSINESS_HOURS = {
    'start': 9,  # 9 AM
    'end': 17    # 5 PM
}


# ===========================
# Chart and Visualization
# ===========================

# Color schemes for different chart types
COLOR_SCHEMES = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'sequential': ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15'],
    'diverging': ['#d7191c', '#fdae61', '#ffffbf', '#abd9e9', '#2c7bb6'],
    'categorical': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                   '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
}

# Chart layout defaults
CHART_CONFIG = {
    'height': 400,
    'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50},
    'font_size': 12,
    'title_font_size': 16,
    'showlegend': True,
    'hovermode': 'closest'
}


# ===========================
# Data Quality and Validation
# ===========================

# Minimum values for data validation
MIN_QUANTITY = 1
MIN_UNIT_PRICE = 0.01
MIN_TOTAL_AMOUNT = 0.01

# Maximum values for data validation
MAX_QUANTITY = 100000
MAX_UNIT_PRICE = 1000000
MAX_TOTAL_AMOUNT = 10000000

# Data types for CSV columns
CSV_COLUMN_DTYPES = {
    'InvoiceNo': str,
    'StockCode': str,
    'Description': str,
    'Quantity': int,
    'InvoiceDate': str,
    'UnitPrice': float,
    'CustomerID': float,  # float to handle NaN
    'Country': str
}

# Required columns in CSV
REQUIRED_CSV_COLUMNS = [
    'InvoiceNo', 'StockCode', 'Description', 'Quantity',
    'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country'
]


# ===========================
# Database Constants
# ===========================

# Table names
TABLE_SALES_TRANSACTIONS = 'sales_transactions'

# Batch size for database operations
DB_BATCH_SIZE = 1000

# Query timeout in seconds
DB_QUERY_TIMEOUT = 30


# ===========================
# ETL Constants
# ===========================

# CSV encoding
CSV_ENCODING = 'ISO-8859-1'

# Cancelled order prefix
CANCELLED_ORDER_PREFIX = 'C'

# Date formats
DATE_FORMAT_INPUT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT_OUTPUT = '%Y-%m-%d'
DATE_FORMAT_DISPLAY = '%B %d, %Y'


# ===========================
# UI/UX Constants
# ===========================

# Metric card settings
METRIC_CARD_CONFIG = {
    'show_delta': True,
    'delta_color': 'normal',
    'border': True
}

# Table settings
TABLE_CONFIG = {
    'max_rows': 100,
    'show_index': False,
    'column_config': {}
}

# Loading messages
LOADING_MESSAGES = {
    'kpis': 'Loading key performance indicators...',
    'revenue': 'Loading revenue data...',
    'customer': 'Loading customer analytics...',
    'product': 'Loading product analytics...',
    'geographic': 'Loading geographic data...'
}

# Error messages
ERROR_MESSAGES = {
    'database_connection': 'Failed to connect to database. Please check your configuration.',
    'no_data': 'No data available to display.',
    'query_failed': 'Failed to execute query. Please try again.',
    'invalid_data': 'Invalid data format detected.'
}


# ===========================
# Performance Constants
# ===========================

# Cache settings
CACHE_TTL_SHORT = 300     # 5 minutes
CACHE_TTL_MEDIUM = 600    # 10 minutes
CACHE_TTL_LONG = 1800     # 30 minutes

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000


# ===========================
# Export Constants
# ===========================

# Export formats
EXPORT_FORMATS = ['CSV', 'Excel', 'JSON']

# File size limits (in MB)
MAX_EXPORT_SIZE_MB = 100

# Export date format
EXPORT_TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'
