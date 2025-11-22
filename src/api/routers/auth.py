"""
Authentication router for user registration, login, and email verification.
"""
from datetime import timedelta
import logging

from fastapi import APIRouter, HTTPException, status

from src.api.auth import (
    Token,
    UserCreate,
    UserLogin,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.api.users import (
    create_user,
    verify_user_email,
    get_user_by_email,
    update_last_login
)
from src.api.email_service import send_verification_email
from src.config.settings import EmailConfig

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Register a new user.

    - **email**: Valid email address (must be unique)
    - **username**: Username (must be unique)
    - **password**: Strong password (min 8 characters recommended)
    - **full_name**: Optional full name

    Returns user details and verification token.
    Email verification required before accessing protected endpoints.
    """
    try:
        # Create user
        new_user = create_user(
            email=user.email,
            username=user.username,
            password=user.password,
            full_name=user.full_name
        )

        logger.info(f"New user registered: {user.email}")

        # Send verification email if enabled
        email_sent = False
        if EmailConfig.EMAIL_ENABLED:
            email_sent = send_verification_email(
                email=new_user['email'],
                verification_token=new_user['verification_token'],
                username=new_user['username']
            )

        response = {
            "message": "User registered successfully. Please verify your email.",
            "user": {
                "id": new_user['id'],
                "email": new_user['email'],
                "username": new_user['username'],
                "full_name": new_user['full_name']
            }
        }

        # In development mode or if email failed, return token for testing
        if not EmailConfig.EMAIL_ENABLED or not email_sent:
            response["verification_token"] = new_user['verification_token']
            response["note"] = "Email sending disabled. For testing, use: POST /api/auth/verify-email?verification_token=<token>"
        else:
            response["note"] = "Verification email sent. Please check your inbox."

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/verify-email")
async def verify_email(verification_token: str):
    """
    Verify user email using token.

    - **verification_token**: Token received during registration

    In production, this would be called via link in verification email.
    """
    success = verify_user_email(verification_token)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )

    return {"message": "Email verified successfully. You can now log in."}


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Login and receive JWT access token.

    - **email**: Registered email address
    - **password**: User password

    Returns JWT token for accessing protected endpoints.
    """
    # Get user from database
    user = get_user_by_email(user_credentials.email)

    # Validate credentials
    if not user or not verify_password(user_credentials.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user['is_active']:
        raise HTTPException(status_code=400, detail="Inactive user account")

    # Check if email is verified
    if not user['is_verified']:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please check your email for verification link."
        )

    # Update last login
    update_last_login(user['email'])

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']},
        expires_delta=access_token_expires
    )

    logger.info(f"User logged in: {user['email']}")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
