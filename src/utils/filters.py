"""
Data filtering utilities for dashboard interactivity.
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from src.database.connection import get_connection
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def get_date_range() -> Tuple[datetime, datetime]:
    """
    Get the min and max dates from the database.

    Returns:
        Tuple[datetime, datetime]: (min_date, max_date)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                MIN(invoice_date) as min_date,
                MAX(invoice_date) as max_date
            FROM sales_transactions
        """)

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result[0], result[1]

    except Exception as e:
        logger.error(f"Error getting date range: {e}")
        # Return default range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date


def get_available_countries() -> List[str]:
    """
    Get list of all available countries from the database.

    Returns:
        List[str]: List of country names sorted alphabetically
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT country
            FROM sales_transactions
            ORDER BY country
        """)

        countries = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return countries

    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        return []


def get_available_products(limit: int = 100) -> List[str]:
    """
    Get list of top products from the database.

    Args:
        limit (int): Maximum number of products to return

    Returns:
        List[str]: List of product descriptions sorted by revenue
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT description
            FROM sales_transactions
            WHERE description IS NOT NULL
            GROUP BY description
            ORDER BY SUM(total_amount) DESC
            LIMIT {limit}
        """)

        products = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        return products

    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return []


def apply_filters(
    query: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    countries: Optional[List[str]] = None,
    products: Optional[List[str]] = None
) -> str:
    """
    Apply filters to a SQL query.

    Args:
        query (str): Base SQL query
        start_date (datetime, optional): Start date filter
        end_date (datetime, optional): End date filter
        countries (List[str], optional): List of countries to filter
        products (List[str], optional): List of products to filter

    Returns:
        str: Modified SQL query with filters applied
    """
    filters = []

    if start_date:
        filters.append(f"invoice_date >= '{start_date.strftime('%Y-%m-%d')}'")

    if end_date:
        filters.append(f"invoice_date <= '{end_date.strftime('%Y-%m-%d')}'")

    if countries and len(countries) > 0:
        country_list = "', '".join(countries)
        filters.append(f"country IN ('{country_list}')")

    if products and len(products) > 0:
        product_list = "', '".join(products)
        filters.append(f"description IN ('{product_list}')")

    if filters:
        if 'WHERE' in query.upper():
            query += " AND " + " AND ".join(filters)
        else:
            query += " WHERE " + " AND ".join(filters)

    logger.debug(f"Applied {len(filters)} filters to query")
    return query


def filter_dataframe(
    df: pd.DataFrame,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    countries: Optional[List[str]] = None,
    products: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Apply filters to a pandas DataFrame.

    Args:
        df (pd.DataFrame): Input dataframe
        start_date (datetime, optional): Start date filter
        end_date (datetime, optional): End date filter
        countries (List[str], optional): List of countries to filter
        products (List[str], optional): List of products to filter

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    filtered_df = df.copy()

    if start_date and 'date' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(start_date)]

    if end_date and 'date' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(end_date)]

    if countries and len(countries) > 0 and 'country' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['country'].isin(countries)]

    if products and len(products) > 0:
        if 'product' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['product'].isin(products)]
        elif 'description' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['description'].isin(products)]

    logger.debug(f"Filtered dataframe from {len(df)} to {len(filtered_df)} rows")
    return filtered_df
