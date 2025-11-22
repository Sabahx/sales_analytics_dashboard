"""
Key Performance Indicators (KPIs) calculation module.
"""
from src.database.connection import get_connection


def get_kpis():
    """
    Get main KPIs: revenue, orders, customers, average order value.

    Returns:
        dict: KPI metrics including revenue, orders, customers, and avg_order
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(total_amount) as revenue,
            COUNT(DISTINCT invoice_no) as orders,
            COUNT(DISTINCT customer_id) as customers
        FROM sales_transactions
    """)

    data = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        'revenue': data[0],
        'orders': data[1],
        'customers': data[2],
        'avg_order': data[0] / data[1]
    }


def get_sales_summary():
    """
    Get comprehensive sales summary with all key metrics.

    Returns:
        dict: Complete sales summary including transactions, products, countries, etc.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as total_transactions,
            COUNT(DISTINCT invoice_no) as total_orders,
            COUNT(DISTINCT customer_id) as total_customers,
            COUNT(DISTINCT description) as total_products,
            COUNT(DISTINCT country) as total_countries,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_transaction,
            MAX(total_amount) as max_transaction,
            MIN(invoice_date) as first_sale,
            MAX(invoice_date) as last_sale
        FROM sales_transactions
    """)

    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        'total_transactions': data[0],
        'total_orders': data[1],
        'total_customers': data[2],
        'total_products': data[3],
        'total_countries': data[4],
        'total_revenue': data[5],
        'avg_transaction': data[6],
        'max_transaction': data[7],
        'first_sale': data[8],
        'last_sale': data[9]
    }
