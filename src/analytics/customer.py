"""
Customer analytics module for segmentation, CLV, and customer insights.
"""
import pandas as pd
from src.database.connection import get_connection


def get_customer_segments():
    """
    Get customer segmentation based on spending levels.

    Returns:
        pd.DataFrame: DataFrame with columns ['segment', 'customers']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            CASE
                WHEN total_spent > 5000 THEN 'VIP (>$5K)'
                WHEN total_spent > 2000 THEN 'High Value ($2K-$5K)'
                WHEN total_spent > 500 THEN 'Medium Value ($500-$2K)'
                ELSE 'Low Value (<$500)'
            END as segment,
            COUNT(*) as customers
        FROM (
            SELECT customer_id, SUM(total_amount) as total_spent
            FROM sales_transactions
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        ) as customer_totals
        GROUP BY segment
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['segment', 'customers'])

    cursor.close()
    conn.close()
    return df


def get_customer_lifetime_value():
    """
    Calculate average customer lifetime value by segment.

    Returns:
        pd.DataFrame: DataFrame with columns ['segment', 'customer_count', 'avg_clv', 'avg_orders', 'avg_order_value']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            CASE
                WHEN total_spent > 5000 THEN 'VIP'
                WHEN total_spent > 2000 THEN 'High Value'
                WHEN total_spent > 500 THEN 'Medium Value'
                ELSE 'Low Value'
            END as segment,
            COUNT(*) as customer_count,
            ROUND(AVG(total_spent)::numeric, 2) as avg_clv,
            ROUND(AVG(order_count)::numeric, 2) as avg_orders,
            ROUND(AVG(total_spent / order_count)::numeric, 2) as avg_order_value
        FROM (
            SELECT
                customer_id,
                SUM(total_amount) as total_spent,
                COUNT(DISTINCT invoice_no) as order_count
            FROM sales_transactions
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        ) as customer_stats
        GROUP BY segment
        ORDER BY avg_clv DESC
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['segment', 'customer_count', 'avg_clv', 'avg_orders', 'avg_order_value'])

    cursor.close()
    conn.close()
    return df


def get_top_customers(limit=10):
    """
    Get top customers by spending.

    Args:
        limit (int): Number of top customers to return

    Returns:
        pd.DataFrame: DataFrame with columns ['customer_id', 'total_spent', 'orders', 'avg_transaction']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            customer_id,
            SUM(total_amount) as total_spent,
            COUNT(DISTINCT invoice_no) as orders,
            AVG(total_amount) as avg_transaction
        FROM sales_transactions
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT {limit}
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['customer_id', 'total_spent', 'orders', 'avg_transaction'])

    cursor.close()
    conn.close()
    return df
