"""
Data extraction module for loading CSV files.
"""
import pandas as pd
from src.config.constants import CSV_ENCODING, REQUIRED_CSV_COLUMNS
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def extract_csv(file_path, encoding=CSV_ENCODING):
    """
    Extract data from CSV file.

    Args:
        file_path (str): Path to CSV file
        encoding (str): File encoding (default: from constants)

    Returns:
        pd.DataFrame: Raw dataframe from CSV

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is missing required columns
    """
    logger.info(f"Loading CSV from {file_path}...")

    try:
        df = pd.read_csv(file_path, encoding=encoding)
        logger.info(f"Loaded {len(df)} rows")

        # Validate required columns
        missing_columns = set(REQUIRED_CSV_COLUMNS) - set(df.columns)
        if missing_columns:
            raise ValueError(f"CSV missing required columns: {missing_columns}")

        logger.debug(f"CSV columns: {list(df.columns)}")
        return df

    except FileNotFoundError:
        logger.error(f"CSV file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        raise
