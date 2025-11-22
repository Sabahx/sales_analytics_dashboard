"""
ETL pipeline runner script.
Extracts data from CSV, transforms it, and loads into database.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.extract import extract_csv
from src.etl.transform import clean_sales_data
from src.etl.load import load_to_database
from src.config.settings import PathConfig
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def run_etl(csv_path):
    """
    Run the complete ETL pipeline.

    Args:
        csv_path (str): Path to the CSV file

    Returns:
        int: Number of rows loaded

    Raises:
        Exception: If ETL pipeline fails
    """
    logger.info("=" * 70)
    logger.info("STARTING ETL PIPELINE")
    logger.info("=" * 70)

    try:
        # Extract
        df = extract_csv(csv_path)

        # Transform
        df_clean = clean_sales_data(df)

        # Load
        rows_inserted = load_to_database(df_clean)

        logger.info("=" * 70)
        logger.info(f"ETL PIPELINE COMPLETE - {rows_inserted} rows loaded")
        logger.info("=" * 70)

        return rows_inserted

    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        raise


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else PathConfig.DEFAULT_CSV_FILE

    logger.info(f"Using CSV file: {csv_file}")
    run_etl(csv_file)
