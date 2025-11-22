"""Analytics module for sales data analysis and forecasting."""

from src.analytics.kpis import get_kpis
from src.analytics.revenue import get_monthly_revenue, get_revenue_trend, get_monthly_growth
from src.analytics.forecasting import (
    get_revenue_forecast,
    get_product_forecast,
    get_country_forecast,
    get_forecast_comparison,
    get_daily_revenue
)

__all__ = [
    'get_kpis',
    'get_monthly_revenue',
    'get_revenue_trend',
    'get_monthly_growth',
    'get_revenue_forecast',
    'get_product_forecast',
    'get_country_forecast',
    'get_forecast_comparison',
    'get_daily_revenue'
]
