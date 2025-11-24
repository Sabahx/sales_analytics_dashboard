"""Forecasting analytics module for sales predictions."""

import pandas as pd
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

from src.database.connection import get_connection
from src.ml.forecasting import SalesForecaster
# from src.ml.ensemble_forecasting import EnsembleForecaster  # Ensemble disabled (didn't improve accuracy)

logger = logging.getLogger(__name__)


def get_daily_revenue(start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Get daily revenue data from the database.

    Args:
        start_date: Optional start date filter (format: 'YYYY-MM-DD')
        end_date: Optional end date filter (format: 'YYYY-MM-DD')

    Returns:
        DataFrame with columns: date, revenue
    """
    conn = get_connection()

    query = """
        SELECT
            DATE(invoice_date) as date,
            SUM(total_amount) as revenue
        FROM sales_transactions
    """

    conditions = []
    if start_date:
        conditions.append(f"invoice_date >= '{start_date}'")
    if end_date:
        conditions.append(f"invoice_date <= '{end_date}'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        GROUP BY DATE(invoice_date)
        ORDER BY date
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['date', 'revenue'])
        cursor.close()
        logger.info(f"Retrieved {len(df)} days of revenue data")
        return df
    except Exception as e:
        logger.error(f"Error fetching daily revenue: {e}")
        raise
    finally:
        conn.close()


def get_revenue_forecast(
    periods: int = 30,
    freq: str = 'D',
    include_history: bool = True,
    seasonality_mode: str = 'multiplicative',
    use_ensemble: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Generate revenue forecast using Ensemble or Prophet.

    Args:
        periods: Number of periods to forecast (default: 30 days)
        freq: Forecast frequency ('D' for daily, 'W' for weekly, 'M' for monthly)
        include_history: Whether to include historical data in the output
        seasonality_mode: 'additive' or 'multiplicative' (default: multiplicative)
        use_ensemble: Whether to use ensemble model (default: True for better accuracy)

    Returns:
        Tuple of (forecast_df, summary_dict)
        - forecast_df: DataFrame with columns: ds (date), yhat (predicted value),
                       yhat_lower (lower bound), yhat_upper (upper bound)
        - summary_dict: Dictionary with forecast summary statistics
    """
    logger.info(f"Generating {periods}-period revenue forecast with frequency '{freq}'")

    # Get historical revenue data
    revenue_df = get_daily_revenue()

    if len(revenue_df) < 30:
        logger.warning("Insufficient historical data for accurate forecasting (minimum 30 days recommended)")

    if use_ensemble:
        # DISABLED: Ensemble didn't improve accuracy (62.33% vs 79.7% for Prophet alone)
        # Fallback to Prophet with optimized parameters
        logger.info("Ensemble disabled - using optimized Prophet instead")
        use_ensemble = False

    if not use_ensemble:
        # Use original Prophet forecaster
        forecaster = SalesForecaster()

        # Prepare data for Prophet without spike detection (simpler is better)
        prophet_df = forecaster.prepare_data(
            revenue_df,
            date_col='date',
            value_col='revenue',
            remove_outliers=False,  # Keep all data
            detect_spikes=False      # Disable spike detection
        )

        # Train model with PRODUCTION-TUNED parameters for Neon dataset
        # Use additive seasonality for volatile retail data (better for high variance)
        forecaster.train(
            prophet_df,
            seasonality_mode='additive',     # Better for volatile data (was multiplicative)
            changepoint_prior_scale=0.18,    # Slightly higher flexibility
            seasonality_prior_scale=12.0,    # Moderate-high seasonality
            add_country_holidays='UK'        # UK holidays
        )
        logger.info("Model training completed with optimized parameters")

        # Generate predictions
        forecast_df = forecaster.predict(periods=periods, freq=freq)

        # Get forecast summary
        summary = forecaster.get_forecast_summary()

        # Calculate accuracy on historical data
        accuracy_metrics = forecaster.calculate_accuracy(prophet_df)
        summary['accuracy_metrics'] = accuracy_metrics

        # Filter to future only if requested
        if not include_history:
            last_date = prophet_df['ds'].max()
            forecast_df = forecast_df[forecast_df['ds'] > last_date]

        logger.info(f"Forecast generated successfully. Average predicted revenue: ${summary['avg_predicted_value']:,.2f}")

        return forecast_df, summary


def get_product_forecast(
    product_code: str,
    periods: int = 30,
    freq: str = 'D'
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Generate forecast for a specific product.

    Args:
        product_code: Stock code of the product
        periods: Number of periods to forecast
        freq: Forecast frequency

    Returns:
        Tuple of (forecast_df, summary_dict)
    """
    logger.info(f"Generating forecast for product: {product_code}")

    conn = get_connection()

    query = """
        SELECT
            DATE(invoice_date) as date,
            SUM(quantity) as quantity
        FROM sales_transactions
        WHERE stock_code = %s
        GROUP BY DATE(invoice_date)
        ORDER BY date
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (product_code,))
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['date', 'quantity'])
        cursor.close()

        if len(df) < 30:
            logger.warning(f"Insufficient data for product {product_code} (minimum 30 days recommended)")
            return pd.DataFrame(), {'error': 'Insufficient historical data'}

        # Initialize forecaster
        forecaster = SalesForecaster()

        # Prepare and train
        prophet_df = forecaster.prepare_data(df, date_col='date', value_col='quantity')
        forecaster.train(prophet_df)

        # Generate predictions
        forecast_df = forecaster.predict(periods=periods, freq=freq)
        summary = forecaster.get_forecast_summary()

        # Filter to future only
        last_date = prophet_df['ds'].max()
        forecast_df = forecast_df[forecast_df['ds'] > last_date]

        logger.info(f"Product forecast completed for {product_code}")

        return forecast_df, summary

    except Exception as e:
        logger.error(f"Error generating product forecast: {e}")
        raise
    finally:
        conn.close()


def get_country_forecast(
    country: str,
    periods: int = 30,
    freq: str = 'D'
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Generate revenue forecast for a specific country.

    Args:
        country: Country name
        periods: Number of periods to forecast
        freq: Forecast frequency

    Returns:
        Tuple of (forecast_df, summary_dict)
    """
    logger.info(f"Generating forecast for country: {country}")

    conn = get_connection()

    query = """
        SELECT
            DATE(invoice_date) as date,
            SUM(total_amount) as revenue
        FROM sales_transactions
        WHERE country = %s
        GROUP BY DATE(invoice_date)
        ORDER BY date
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (country,))
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['date', 'revenue'])
        cursor.close()

        if len(df) < 30:
            logger.warning(f"Insufficient data for country {country}")
            return pd.DataFrame(), {'error': 'Insufficient historical data'}

        # Initialize forecaster
        forecaster = SalesForecaster()

        # Prepare and train
        prophet_df = forecaster.prepare_data(df, date_col='date', value_col='revenue')
        forecaster.train(prophet_df)

        # Generate predictions
        forecast_df = forecaster.predict(periods=periods, freq=freq)
        summary = forecaster.get_forecast_summary()

        # Filter to future only
        last_date = prophet_df['ds'].max()
        forecast_df = forecast_df[forecast_df['ds'] > last_date]

        logger.info(f"Country forecast completed for {country}")

        return forecast_df, summary

    except Exception as e:
        logger.error(f"Error generating country forecast: {e}")
        raise
    finally:
        conn.close()


def get_forecast_comparison(use_ensemble: bool = True) -> pd.DataFrame:
    """
    Compare actual vs predicted values for the last 30 days.
    Useful for validating forecast accuracy.

    Args:
        use_ensemble: Whether to use ensemble model (default: True)

    Returns:
        DataFrame with columns: date, actual_revenue, predicted_revenue, difference, difference_pct
    """
    logger.info("Generating forecast comparison")

    # Get all historical data
    revenue_df = get_daily_revenue()

    if len(revenue_df) < 60:
        logger.warning("Insufficient data for comparison (minimum 60 days needed)")
        return pd.DataFrame()

    # Split into training and test sets
    split_point = len(revenue_df) - 30
    train_df = revenue_df.iloc[:split_point].copy()
    test_df = revenue_df.iloc[split_point:].copy()

    if use_ensemble:
        # DISABLED: Ensemble didn't improve accuracy (62.33% vs Prophet alone)
        logger.info("Ensemble disabled - using optimized Prophet instead")
        use_ensemble = False

    if not use_ensemble:
        # Use original Prophet forecaster
        forecaster = SalesForecaster()

        # Prepare training data without spike detection
        prophet_train = forecaster.prepare_data(
            train_df,
            date_col='date',
            value_col='revenue',
            remove_outliers=False,
            detect_spikes=False
        )

        # Train model with optimized parameters
        forecaster.train(
            prophet_train,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.30,  # High flexibility (tuned)
            seasonality_prior_scale=5.0,   # Lower seasonality (tuned)
            add_country_holidays='UK'
        )

        # Generate predictions
        forecast_df = forecaster.predict(periods=30, freq='D')

        # Merge actual and predicted
        last_train_date = prophet_train['ds'].max()
        forecast_future = forecast_df[forecast_df['ds'] > last_train_date][['ds', 'yhat']].copy()

    # Convert test_df date to datetime for proper merging
    test_df['date'] = pd.to_datetime(test_df['date'])

    comparison = test_df.merge(
        forecast_future,
        left_on='date',
        right_on='ds',
        how='inner'
    )

    # Convert revenue to float to avoid Decimal/float type issues
    comparison['revenue'] = comparison['revenue'].astype(float)
    comparison['yhat'] = comparison['yhat'].astype(float)

    comparison['difference'] = comparison['revenue'] - comparison['yhat']
    comparison['difference_pct'] = (comparison['difference'] / comparison['revenue']) * 100

    comparison = comparison.rename(columns={
        'revenue': 'actual_revenue',
        'yhat': 'predicted_revenue'
    })

    comparison = comparison[['date', 'actual_revenue', 'predicted_revenue', 'difference', 'difference_pct']]

    logger.info("Forecast comparison completed")

    return comparison
