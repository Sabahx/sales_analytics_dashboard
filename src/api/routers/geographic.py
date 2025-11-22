"""
Geographic analytics router for country and regional performance.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_current_verified_user
from src.analytics.geographic import (
    get_revenue_by_country,
    get_country_performance_detailed
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/geographic",
    tags=["Geographic"]
)


@router.get("/revenue-by-country")
async def get_revenue_by_country_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get top 10 countries by revenue.

    Returns:
    - country: Country name
    - revenue: Total revenue

    Requires authentication.
    """
    try:
        revenue_by_country = get_revenue_by_country()
        return {
            "revenue_by_country": revenue_by_country.to_dict(orient='records'),
            "count": len(revenue_by_country),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching revenue by country: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch revenue by country")


@router.get("/country-performance")
async def get_country_performance_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get detailed country performance metrics.

    Returns:
    - country: Country name
    - orders: Number of orders
    - customers: Number of unique customers
    - revenue: Total revenue
    - avg_transaction: Average transaction value
    - units_sold: Total units sold

    Shows top 15 countries by revenue.

    Requires authentication.
    """
    try:
        country_performance = get_country_performance_detailed()
        return {
            "country_performance": country_performance.to_dict(orient='records'),
            "count": len(country_performance),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching country performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch country performance")
