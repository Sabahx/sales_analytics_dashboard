"""
Product analytics module for product performance analysis.
"""
import pandas as pd
from src.database.connection import get_connection


def get_top_products(limit=10):
    """
    Get top products by revenue.

    Args:
        limit (int): Number of top products to return

    Returns:
        pd.DataFrame: DataFrame with columns ['product', 'revenue', 'units_sold', 'orders']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT description as product,
               SUM(total_amount) as revenue,
               SUM(quantity) as units_sold,
               COUNT(DISTINCT invoice_no) as orders
        FROM sales_transactions
        GROUP BY description
        ORDER BY revenue DESC
        LIMIT {limit}
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['product', 'revenue', 'units_sold', 'orders'])

    cursor.close()
    conn.close()
    return df
