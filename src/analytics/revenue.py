"""
Revenue analytics module for trend analysis and growth calculations.
"""
import pandas as pd
from src.database.connection import get_connection


def get_revenue_trend():
    """
    Get daily revenue trend.

    Returns:
        pd.DataFrame: DataFrame with columns ['date', 'revenue']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE(invoice_date) as date, SUM(total_amount) as revenue
        FROM sales_transactions
        GROUP BY DATE(invoice_date)
        ORDER BY date
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['date', 'revenue'])

    cursor.close()
    conn.close()
    return df


def get_monthly_revenue():
    """
    Get monthly revenue and order counts.

    Returns:
        pd.DataFrame: DataFrame with columns ['month', 'revenue', 'orders']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            TO_CHAR(invoice_date, 'YYYY-MM') as month,
            SUM(total_amount) as revenue,
            COUNT(DISTINCT invoice_no) as orders
        FROM sales_transactions
        GROUP BY TO_CHAR(invoice_date, 'YYYY-MM')
        ORDER BY month
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['month', 'revenue', 'orders'])

    cursor.close()
    conn.close()
    return df


def get_monthly_growth():
    """
    Calculate month-over-month growth rate.

    Returns:
        pd.DataFrame: DataFrame with columns ['month', 'revenue', 'prev_month_revenue', 'growth_rate']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            month,
            revenue,
            LAG(revenue) OVER (ORDER BY month) as prev_month_revenue,
            ROUND(
                ((revenue - LAG(revenue) OVER (ORDER BY month)) /
                LAG(revenue) OVER (ORDER BY month) * 100)::numeric,
                2
            ) as growth_rate
        FROM (
            SELECT
                TO_CHAR(invoice_date, 'YYYY-MM') as month,
                SUM(total_amount) as revenue
            FROM sales_transactions
            GROUP BY month
        ) monthly_data
        ORDER BY month
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['month', 'revenue', 'prev_month_revenue', 'growth_rate'])

    cursor.close()
    conn.close()
    return df


def get_sales_by_hour():
    """
    Get sales pattern by hour of day.

    Returns:
        pd.DataFrame: DataFrame with columns ['hour', 'revenue', 'transactions']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            EXTRACT(HOUR FROM invoice_date) as hour,
            SUM(total_amount) as revenue,
            COUNT(*) as transactions
        FROM sales_transactions
        GROUP BY hour
        ORDER BY hour
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['hour', 'revenue', 'transactions'])

    cursor.close()
    conn.close()
    return df


def get_sales_by_day_of_week():
    """
    Get sales pattern by day of week.

    Returns:
        pd.DataFrame: DataFrame with columns ['day_name', 'day_num', 'revenue', 'orders']
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            TO_CHAR(invoice_date, 'Day') as day_name,
            EXTRACT(DOW FROM invoice_date) as day_num,
            SUM(total_amount) as revenue,
            COUNT(DISTINCT invoice_no) as orders
        FROM sales_transactions
        GROUP BY day_name, day_num
        ORDER BY day_num
    """)

    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['day_name', 'day_num', 'revenue', 'orders'])

    cursor.close()
    conn.close()
    return df
