"""
Shared dependencies for API endpoints.
Contains authentication and authorization dependencies.
"""
from fastapi import Depends, HTTPException, status

from src.api.auth import oauth2_scheme, decode_access_token
from src.api.users import get_user_by_email


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency to extract and validate current user from JWT token.

    Args:
        token: JWT token from Authorization header

    Returns:
        User dictionary if valid

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    user = get_user_by_email(email)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure current user is active.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User dictionary if active

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user['is_active']:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_verified_user(current_user: dict = Depends(get_current_active_user)) -> dict:
    """
    Dependency to ensure current user has verified their email.

    Args:
        current_user: User from get_current_active_user dependency

    Returns:
        User dictionary if verified

    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user['is_verified']:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please check your email for verification link."
        )
    return current_user
