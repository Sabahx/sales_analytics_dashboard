"""
Product analytics router for product performance and insights.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import get_current_verified_user
from src.analytics.product import get_top_products

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.get("/top")
async def get_top_products_endpoint(
    limit: int = Query(default=10, ge=1, le=100, description="Number of top products to return"),
    current_user: dict = Depends(get_current_verified_user)
):
    """
    Get top products by revenue.

    - **limit**: Number of top products to return (1-100, default: 10)

    Returns:
    - product: Product name/description
    - revenue: Total revenue generated
    - units_sold: Total units sold
    - orders: Number of orders containing this product

    Requires authentication.
    """
    try:
        top_products = get_top_products(limit=limit)
        return {
            "top_products": top_products.to_dict(orient='records'),
            "count": len(top_products),
            "requested_by": current_user['email']
        }
    except Exception as e:
        logger.error(f"Error fetching top products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch top products")
