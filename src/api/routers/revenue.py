"""
Revenue analytics router for revenue trends, growth, and patterns.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_current_verified_user
from src.analytics.revenue import (
    get_revenue_trend,
    get_monthly_revenue,
    get_monthly_growth,
    get_sales_by_hour,
    get_sales_by_day_of_week
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/revenue",
    tags=["Revenue"]
)


@router.get("/daily-trend")
async def get_daily_revenue_trend(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get daily revenue trend.

    Returns:
    - date: Transaction date
    - revenue: Total revenue for that day

    Requires authentication.
    """
    try:
        revenue_trend = get_revenue_trend()
        return {
            "daily_revenue": revenue_trend.to_dict(orient='records'),
            "count": len(revenue_trend),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching daily revenue trend: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch daily revenue trend")


@router.get("/monthly")
async def get_monthly_revenue_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get monthly revenue with order counts.

    Returns:
    - month: Month in YYYY-MM format
    - revenue: Total revenue
    - orders: Number of orders

    Requires authentication.
    """
    try:
        monthly_revenue = get_monthly_revenue()
        return {
            "monthly_revenue": monthly_revenue.to_dict(orient='records'),
            "count": len(monthly_revenue),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching monthly revenue: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monthly revenue")


@router.get("/growth")
async def get_monthly_growth_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get month-over-month revenue growth rate.

    Returns:
    - month: Month in YYYY-MM format
    - revenue: Current month revenue
    - prev_month_revenue: Previous month revenue
    - growth_rate: Growth percentage

    Requires authentication.
    """
    try:
        monthly_growth = get_monthly_growth()
        return {
            "monthly_growth": monthly_growth.to_dict(orient='records'),
            "count": len(monthly_growth),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching monthly growth: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monthly growth")


@router.get("/by-hour")
async def get_sales_by_hour_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get sales pattern by hour of day.

    Returns:
    - hour: Hour of day (0-23)
    - revenue: Total revenue
    - transactions: Number of transactions

    Useful for identifying peak sales hours.

    Requires authentication.
    """
    try:
        sales_by_hour = get_sales_by_hour()
        return {
            "sales_by_hour": sales_by_hour.to_dict(orient='records'),
            "count": len(sales_by_hour),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching sales by hour: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sales by hour")


@router.get("/by-day-of-week")
async def get_sales_by_day_of_week_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get sales pattern by day of week.

    Returns:
    - day_name: Day name (Monday, Tuesday, etc.)
    - day_num: Day number (0=Sunday, 6=Saturday)
    - revenue: Total revenue
    - orders: Number of orders

    Useful for identifying best performing days.

    Requires authentication.
    """
    try:
        sales_by_day = get_sales_by_day_of_week()
        return {
            "sales_by_day": sales_by_day.to_dict(orient='records'),
            "count": len(sales_by_day),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching sales by day of week: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sales by day of week")
