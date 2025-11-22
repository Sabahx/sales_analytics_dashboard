"""
Geographic analytics module for country and regional performance analysis.
"""
import pandas as pd
from src.database.connection import get_connection


def get_revenue_by_country():
    """
    Get revenue by country (top 10).

    Returns:
        pd.DataFrame: DataFrame with columns ['country', 'revenue']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT country, SUM(total_amount) as revenue
        FROM sales_transactions
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 10
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['country', 'revenue'])

    cursor.close()
    conn.close()
    return df


def get_country_performance_detailed():
    """
    Get detailed country performance metrics.

    Returns:
        pd.DataFrame: DataFrame with columns ['country', 'orders', 'customers', 'revenue', 'avg_transaction', 'units_sold']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            country,
            COUNT(DISTINCT invoice_no) as orders,
            COUNT(DISTINCT customer_id) as customers,
            SUM(total_amount) as revenue,
            ROUND(AVG(total_amount)::numeric, 2) as avg_transaction,
            SUM(quantity) as units_sold
        FROM sales_transactions
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 15
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['country', 'orders', 'customers', 'revenue', 'avg_transaction', 'units_sold'])

    cursor.close()
    conn.close()
    return df
