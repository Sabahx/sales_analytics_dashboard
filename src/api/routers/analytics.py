"""
Analytics router for sales analytics and forecasting endpoints.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_current_verified_user
from src.analytics import (
    get_kpis,
    get_monthly_revenue,
    get_revenue_forecast
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get("/kpis")
async def get_analytics_kpis(current_user: dict = Depends(get_current_verified_user)):
    """
    Get key performance indicators (KPIs).

    Returns:
    - Total revenue
    - Total transactions
    - Average order value
    - Total customers
    - Total products sold

    Requires authentication.
    """
    try:
        kpis = get_kpis()
        return {
            "kpis": kpis,
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching KPIs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch KPIs")


@router.get("/revenue/monthly")
async def get_analytics_monthly_revenue(current_user: dict = Depends(get_current_verified_user)):
    """
    Get monthly revenue breakdown.

    Returns monthly revenue aggregated by month.

    Requires authentication.
    """
    try:
        monthly_revenue = get_monthly_revenue()
        return {
            "monthly_revenue": monthly_revenue.to_dict(orient='records'),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching monthly revenue: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monthly revenue")


@router.get("/forecast/revenue")
async def get_analytics_revenue_forecast(
    periods: int = 30,
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get revenue forecast using Prophet ML model.

    - **periods**: Number of days to forecast (default: 30)

    Returns:
    - Forecasted revenue with confidence intervals
    - Model accuracy: 63.6%

    Requires authentication.
    """
    try:
        forecast_df, summary = get_revenue_forecast(periods=periods, include_history=False)

        return {
            "forecast": forecast_df.to_dict(orient='records'),
            "summary": summary,
            "model_accuracy": "63.6%",
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate forecast")
