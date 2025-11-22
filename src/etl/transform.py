"""
Data transformation module for cleaning and preparing data.
"""
import pandas as pd
from src.config.constants import CANCELLED_ORDER_PREFIX, MIN_QUANTITY, MIN_UNIT_PRICE
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def clean_sales_data(df):
    """
    Clean sales transaction data.

    Args:
        df (pd.DataFrame): Raw dataframe

    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    logger.info(f"Cleaning data... Initial rows: {len(df)}")
    initial_rows = len(df)

    # Remove cancelled orders (starting with 'C')
    df = df[~df['InvoiceNo'].astype(str).str.startswith(CANCELLED_ORDER_PREFIX)]
    cancelled_removed = initial_rows - len(df)
    logger.debug(f"Removed {cancelled_removed} cancelled orders")

    # Remove negative quantities
    df = df[df['Quantity'] >= MIN_QUANTITY]
    negative_removed = initial_rows - cancelled_removed - len(df)
    logger.debug(f"Removed {negative_removed} rows with invalid quantities")

    # Remove zero prices
    df = df[df['UnitPrice'] >= MIN_UNIT_PRICE]
    zero_price_removed = initial_rows - cancelled_removed - negative_removed - len(df)
    logger.debug(f"Removed {zero_price_removed} rows with invalid prices")

    # Calculate total amount
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']

    # Convert date
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    logger.info(f"Clean data complete: {len(df)} rows (removed {initial_rows - len(df)} rows)")
    return df
