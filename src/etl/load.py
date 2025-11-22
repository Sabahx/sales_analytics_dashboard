"""
Data loading module for inserting data into PostgreSQL database.
"""
import pandas as pd
from src.database.connection import get_connection
from src.config.constants import TABLE_SALES_TRANSACTIONS, DB_BATCH_SIZE
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def load_to_database(df):
    """
    Load cleaned dataframe into PostgreSQL database.

    Args:
        df (pd.DataFrame): Cleaned dataframe to load

    Returns:
        int: Number of rows inserted

    Raises:
        Exception: If database insertion fails
    """
    logger.info("Connecting to database...")
    conn = get_connection()
    cursor = conn.cursor()

    logger.info(f"Inserting {len(df)} rows into {TABLE_SALES_TRANSACTIONS}...")
    count = 0

    try:
        for _, row in df.iterrows():
            cursor.execute(f"""
                INSERT INTO {TABLE_SALES_TRANSACTIONS}
                (invoice_no, stock_code, description, quantity, invoice_date,
                 unit_price, customer_id, country, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['InvoiceNo'],
                row['StockCode'],
                row['Description'] if pd.notna(row['Description']) else 'Unknown',
                int(row['Quantity']),
                row['InvoiceDate'],
                float(row['UnitPrice']),
                int(row['CustomerID']) if pd.notna(row['CustomerID']) else None,
                row['Country'],
                float(row['TotalAmount'])
            ))
            count += 1
            if count % DB_BATCH_SIZE == 0:
                logger.info(f"  Inserted {count} rows...")

        conn.commit()
        logger.info(f"Successfully inserted {count} rows total")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error during database insertion: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

    return count
