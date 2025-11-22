"""
Export utilities for generating reports in various formats.
"""
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import io
from src.config.constants import EXPORT_TIMESTAMP_FORMAT
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def export_to_csv(df: pd.DataFrame, filename: str = None) -> bytes:
    """
    Export DataFrame to CSV format.

    Args:
        df (pd.DataFrame): Data to export
        filename (str, optional): Custom filename

    Returns:
        bytes: CSV data as bytes
    """
    try:
        if filename is None:
            timestamp = datetime.now().strftime(EXPORT_TIMESTAMP_FORMAT)
            filename = f"sales_data_{timestamp}.csv"

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue().encode('utf-8')

        logger.info(f"Exported {len(df)} rows to CSV: {filename}")
        return csv_data

    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise


def export_to_excel(df: pd.DataFrame, filename: str = None) -> bytes:
    """
    Export DataFrame to Excel format.

    Args:
        df (pd.DataFrame): Data to export
        filename (str, optional): Custom filename

    Returns:
        bytes: Excel data as bytes
    """
    try:
        if filename is None:
            timestamp = datetime.now().strftime(EXPORT_TIMESTAMP_FORMAT)
            filename = f"sales_data_{timestamp}.xlsx"

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sales Data')

        excel_data = excel_buffer.getvalue()

        logger.info(f"Exported {len(df)} rows to Excel: {filename}")
        return excel_data

    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise


def create_summary_report(kpis: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a summary report DataFrame from KPIs.

    Args:
        kpis (Dict[str, Any]): KPI metrics

    Returns:
        pd.DataFrame: Summary report
    """
    try:
        report_data = {
            'Metric': [
                'Total Revenue',
                'Total Orders',
                'Total Customers',
                'Average Order Value'
            ],
            'Value': [
                f"${kpis.get('revenue', 0):,.2f}",
                f"{kpis.get('orders', 0):,}",
                f"{kpis.get('customers', 0):,}",
                f"${kpis.get('avg_order', 0):,.2f}"
            ]
        }

        df = pd.DataFrame(report_data)
        logger.info("Created summary report")
        return df

    except Exception as e:
        logger.error(f"Error creating summary report: {e}")
        raise


def format_for_export(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format DataFrame for export (clean column names, format numbers, etc.).

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        pd.DataFrame: Formatted dataframe
    """
    try:
        df_export = df.copy()

        # Clean column names (remove underscores, title case)
        df_export.columns = [col.replace('_', ' ').title() for col in df_export.columns]

        # Round numeric columns to 2 decimal places
        numeric_columns = df_export.select_dtypes(include=['float64', 'float32']).columns
        df_export[numeric_columns] = df_export[numeric_columns].round(2)

        # Format datetime columns
        datetime_columns = df_export.select_dtypes(include=['datetime64']).columns
        for col in datetime_columns:
            df_export[col] = df_export[col].dt.strftime('%Y-%m-%d %H:%M:%S')

        logger.debug("Formatted dataframe for export")
        return df_export

    except Exception as e:
        logger.error(f"Error formatting dataframe: {e}")
        return df
