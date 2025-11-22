"""
Users router for user profile and account management endpoints.
"""
from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_verified_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_verified_user)):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return {
        "id": current_user['id'],
        "email": current_user['email'],
        "username": current_user['username'],
        "full_name": current_user['full_name'],
        "is_active": current_user['is_active'],
        "is_verified": current_user['is_verified'],
        "is_superuser": current_user['is_superuser'],
        "created_at": current_user['created_at'],
        "last_login": current_user['last_login']
    }
