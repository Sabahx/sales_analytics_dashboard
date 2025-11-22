"""
Customer analytics router for customer insights, segmentation, and CLV.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import get_current_verified_user
from src.analytics.customer import (
    get_customer_segments,
    get_customer_lifetime_value,
    get_top_customers
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/customers",
    tags=["Customers"]
)


@router.get("/top")
async def get_top_customers_endpoint(
    limit: int = Query(default=10, ge=1, le=100, description="Number of top customers to return"),
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get top customers by total spending.

    - **limit**: Number of top customers to return (1-100, default: 10)

    Returns:
    - customer_id: Customer identifier
    - total_spent: Total amount spent
    - orders: Number of orders
    - avg_transaction: Average transaction value

    Requires authentication.
    """
    try:
        top_customers = get_top_customers(limit=limit)
        return {
            "top_customers": top_customers.to_dict(orient='records'),
            "count": len(top_customers),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching top customers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch top customers")


@router.get("/segments")
async def get_customer_segments_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get customer segmentation based on spending levels.

    Segments:
    - VIP (>$5K)
    - High Value ($2K-$5K)
    - Medium Value ($500-$2K)
    - Low Value (<$500)

    Returns customer count per segment.

    Requires authentication.
    """
    try:
        segments = get_customer_segments()
        return {
            "segments": segments.to_dict(orient='records'),
            "total_segments": len(segments),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching customer segments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch customer segments")


@router.get("/lifetime-value")
async def get_customer_lifetime_value_endpoint(
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get customer lifetime value (CLV) analysis by segment.

    Returns:
    - segment: Customer segment
    - customer_count: Number of customers in segment
    - avg_clv: Average customer lifetime value
    - avg_orders: Average number of orders
    - avg_order_value: Average order value

    Requires authentication.
    """
    try:
        clv_data = get_customer_lifetime_value()
        return {
            "lifetime_value": clv_data.to_dict(orient='records'),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching customer lifetime value: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch customer lifetime value")
