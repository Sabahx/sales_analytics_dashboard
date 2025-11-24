"""
Machine Learning forecasting module using Prophet for time-series prediction.
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import warnings

# NumPy 2.x compatibility patch for Prophet
if not hasattr(np, 'float_'):
    np.float_ = np.float64
if not hasattr(np, 'int_'):
    np.int_ = np.int64

# Suppress cmdstanpy and Prophet warnings
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
logging.getLogger('prophet').setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

from prophet import Prophet
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


class SalesForecaster:
    """
    Sales forecasting using Facebook Prophet.

    Provides revenue predictions, confidence intervals, and trend analysis.
    """

    def __init__(self):
        """Initialize the forecaster with default Prophet settings."""
        self.model = None
        self.forecast_df = None
        self.trained = False

    def prepare_data(self, df: pd.DataFrame, date_col: str = 'date', value_col: str = 'revenue',
                     remove_outliers: bool = True, detect_spikes: bool = True) -> pd.DataFrame:
        """
        Prepare data for Prophet with spike detection (requires 'ds' and 'y' columns).

        Args:
            df (pd.DataFrame): Input dataframe
            date_col (str): Name of date column
            value_col (str): Name of value column
            remove_outliers (bool): Whether to remove outliers using IQR method
            detect_spikes (bool): Whether to detect and mark revenue spikes

        Returns:
            pd.DataFrame: Prepared dataframe with 'ds', 'y', and optional spike columns
        """
        try:
            prophet_df = pd.DataFrame({
                'ds': pd.to_datetime(df[date_col]),
                'y': pd.to_numeric(df[value_col], errors='coerce')  # Convert to float, handle Decimals
            })

            # Remove any nulls
            prophet_df = prophet_df.dropna()

            # Detect spikes BEFORE removing them (keep them but learn from them)
            if detect_spikes and len(prophet_df) > 30:
                # Calculate rolling mean and std (7-day window)
                prophet_df['rolling_mean'] = prophet_df['y'].rolling(window=7, center=True).mean()
                prophet_df['rolling_std'] = prophet_df['y'].rolling(window=7, center=True).std()

                # Fill NaN values from rolling calculation
                prophet_df['rolling_mean'].fillna(prophet_df['y'].mean(), inplace=True)
                prophet_df['rolling_std'].fillna(prophet_df['y'].std(), inplace=True)

                # Identify spikes: values > 2 std deviations above rolling mean
                threshold = prophet_df['rolling_mean'] + (2 * prophet_df['rolling_std'])
                prophet_df['is_spike'] = (prophet_df['y'] > threshold).astype(int)

                spike_count = prophet_df['is_spike'].sum()
                if spike_count > 0:
                    logger.info(f"Detected {spike_count} revenue spikes (will be learned as events)")

                # Clean up temporary columns
                prophet_df = prophet_df.drop(['rolling_mean', 'rolling_std'], axis=1)

            # Remove outliers using IQR method (only if explicitly enabled)
            if remove_outliers and len(prophet_df) > 30:
                Q1 = prophet_df['y'].quantile(0.25)
                Q3 = prophet_df['y'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR

                original_len = len(prophet_df)
                prophet_df = prophet_df[(prophet_df['y'] >= lower_bound) & (prophet_df['y'] <= upper_bound)]
                removed = original_len - len(prophet_df)

                if removed > 0:
                    logger.info(f"Removed {removed} outliers")

            # Sort by date
            prophet_df = prophet_df.sort_values('ds')

            logger.info(f"Prepared {len(prophet_df)} records for forecasting")
            return prophet_df

        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise

    def train(
        self,
        df: pd.DataFrame,
        seasonality_mode: str = 'multiplicative',
        changepoint_prior_scale: float = 0.08,  # Conservative for production
        seasonality_prior_scale: float = 8.0,    # Moderate seasonality (tuned for Neon data)
        add_country_holidays: str = 'UK'
    ) -> None:
        """
        Train the Prophet model on historical data with balanced parameters.

        Args:
            df (pd.DataFrame): Training data with 'ds' and 'y' columns
            seasonality_mode (str): 'additive' or 'multiplicative'
            changepoint_prior_scale (float): Flexibility of trend (0.001-0.5)
            seasonality_prior_scale (float): Strength of seasonality (0.01-10)
            add_country_holidays (str): Country code for holidays ('UK', 'US', etc.)
        """
        try:
            logger.info("Training Prophet model with balanced parameters...")

            # Initialize model with conservative settings
            self.model = Prophet(
                seasonality_mode=seasonality_mode,
                changepoint_prior_scale=changepoint_prior_scale,
                seasonality_prior_scale=seasonality_prior_scale,
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=True,
                interval_width=0.95  # 95% confidence interval
            )

            # Add country holidays (helps with special days)
            if add_country_holidays:
                try:
                    self.model.add_country_holidays(country_name=add_country_holidays)
                    logger.info(f"Added {add_country_holidays} holidays to model")
                except Exception as e:
                    logger.warning(f"Could not add holidays: {e}")

            # Add only monthly seasonality (quarterly was too aggressive)
            self.model.add_seasonality(name='monthly', period=30.5, fourier_order=5)

            # Add spike regressor if present (helps model learn high-revenue patterns)
            if 'is_spike' in df.columns:
                self.model.add_regressor('is_spike', prior_scale=0.5, mode='additive')

                # Calculate spike patterns by day of week for future predictions
                df['dow'] = df['ds'].dt.dayofweek
                spike_by_dow = df.groupby('dow')['is_spike'].mean()
                self.spike_patterns = spike_by_dow.to_dict()

                logger.info(f"Added spike regressor. Spike patterns by day: {self.spike_patterns}")
                df = df.drop('dow', axis=1)

            # Fit the model
            self.model.fit(df)
            self.trained = True

            logger.info("Model training completed successfully")

        except Exception as e:
            import traceback
            logger.error(f"Error training model: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def predict(self, periods: int = 30, freq: str = 'D') -> pd.DataFrame:
        """
        Generate forecasts for future periods.

        Args:
            periods (int): Number of periods to forecast
            freq (str): Frequency ('D' for daily, 'W' for weekly, 'M' for monthly)

        Returns:
            pd.DataFrame: Forecast with predictions and confidence intervals
        """
        try:
            if not self.trained:
                raise ValueError("Model must be trained before making predictions")

            logger.info(f"Generating forecast for {periods} periods")

            # Create future dataframe
            future = self.model.make_future_dataframe(periods=periods, freq=freq)

            # Add spike regressor for future dates if it was used in training
            if hasattr(self.model, 'extra_regressors') and 'is_spike' in self.model.extra_regressors:
                # Smart spike prediction: use day-of-week patterns from historical data
                # Get spike probability by day of week from training data
                if hasattr(self, 'spike_patterns'):
                    future['dow'] = future['ds'].dt.dayofweek
                    future['is_spike'] = future['dow'].map(self.spike_patterns).fillna(0)
                    logger.info(f"Applied day-of-week spike patterns to future predictions")
                else:
                    # Fallback: no spike prediction
                    future['is_spike'] = 0
                future = future.drop('dow', axis=1, errors='ignore')

            # Make predictions
            self.forecast_df = self.model.predict(future)

            logger.info(f"Forecast generated: {len(self.forecast_df)} data points")
            return self.forecast_df

        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            raise

    def get_forecast_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics from the forecast.

        Returns:
            Dict[str, Any]: Summary metrics
        """
        try:
            if self.forecast_df is None:
                raise ValueError("No forecast available. Run predict() first.")

            # Get future predictions only
            future_df = self.forecast_df[self.forecast_df['ds'] > self.forecast_df['ds'].iloc[-1] - pd.Timedelta(days=30)]

            summary = {
                'avg_predicted_value': future_df['yhat'].mean(),
                'total_predicted_value': future_df['yhat'].sum(),
                'min_predicted_value': future_df['yhat'].min(),
                'max_predicted_value': future_df['yhat'].max(),
                'avg_uncertainty': (future_df['yhat_upper'] - future_df['yhat_lower']).mean(),
                'trend_direction': 'increasing' if future_df['trend'].iloc[-1] > future_df['trend'].iloc[0] else 'decreasing'
            }

            logger.debug(f"Generated forecast summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise

    def get_forecast_dataframe(self, future_only: bool = True) -> pd.DataFrame:
        """
        Get the forecast dataframe with predictions.

        Args:
            future_only (bool): Return only future predictions

        Returns:
            pd.DataFrame: Forecast data
        """
        try:
            if self.forecast_df is None:
                raise ValueError("No forecast available. Run predict() first.")

            df = self.forecast_df.copy()

            if future_only:
                # Get only future predictions
                last_historical_date = df['ds'].iloc[-31] if len(df) > 30 else df['ds'].iloc[0]
                df = df[df['ds'] > last_historical_date]

            # Select relevant columns
            df = df[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend']]
            df.columns = ['date', 'predicted', 'lower_bound', 'upper_bound', 'trend']

            return df

        except Exception as e:
            logger.error(f"Error getting forecast dataframe: {e}")
            raise

    def calculate_accuracy(self, actual_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate forecast accuracy metrics.

        Args:
            actual_df (pd.DataFrame): Actual values with 'ds' and 'y' columns

        Returns:
            Dict[str, float]: Accuracy metrics (MAE, RMSE, MAPE)
        """
        try:
            if self.forecast_df is None:
                raise ValueError("No forecast available")

            # Merge actual and predicted
            merged = pd.merge(
                actual_df,
                self.forecast_df[['ds', 'yhat']],
                on='ds',
                how='inner'
            )

            # Convert to float to avoid Decimal/float type issues
            merged['y'] = merged['y'].astype(float)
            merged['yhat'] = merged['yhat'].astype(float)

            # Calculate metrics
            mae = np.mean(np.abs(merged['y'] - merged['yhat']))
            rmse = np.sqrt(np.mean((merged['y'] - merged['yhat']) ** 2))
            mape = np.mean(np.abs((merged['y'] - merged['yhat']) / merged['y'])) * 100

            accuracy = {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'accuracy_percent': 100 - mape
            }

            logger.info(f"Accuracy metrics: MAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape:.2f}%")
            return accuracy

        except Exception as e:
            logger.error(f"Error calculating accuracy: {e}")
            raise


def quick_forecast(
    df: pd.DataFrame,
    date_col: str = 'date',
    value_col: str = 'revenue',
    periods: int = 30
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Quick forecast function for easy use.

    Args:
        df (pd.DataFrame): Historical data
        date_col (str): Date column name
        value_col (str): Value column name
        periods (int): Number of periods to forecast

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: (forecast_df, summary)
    """
    try:
        forecaster = SalesForecaster()

        # Prepare data
        prophet_df = forecaster.prepare_data(df, date_col, value_col)

        # Train model
        forecaster.train(prophet_df)

        # Generate forecast
        forecaster.predict(periods=periods)

        # Get results
        forecast_df = forecaster.get_forecast_dataframe(future_only=True)
        summary = forecaster.get_forecast_summary()

        return forecast_df, summary

    except Exception as e:
        logger.error(f"Error in quick forecast: {e}")
        raise
