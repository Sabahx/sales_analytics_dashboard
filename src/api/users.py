"""
User database operations for authentication and user management.
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

from src.database.connection import get_connection
from src.api.auth import get_password_hash, generate_verification_token

logger = logging.getLogger(__name__)


def get_user_by_email(email: str) -> Optional[dict]:
   
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, email, username, hashed_password, full_name,
                   is_active, is_verified, is_superuser, created_at, last_login
            FROM users
            WHERE email = %s
            """,
            (email,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return {
                'id': row[0],
                'email': row[1],
                'username': row[2],
                'hashed_password': row[3],
                'full_name': row[4],
                'is_active': row[5],
                'is_verified': row[6],
                'is_superuser': row[7],
                'created_at': row[8],
                'last_login': row[9]
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching user by email: {e}")
        raise
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[dict]:

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, email, username, hashed_password, full_name,
                   is_active, is_verified, is_superuser, created_at, last_login
            FROM users
            WHERE username = %s
            """,
            (username,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return {
                'id': row[0],
                'email': row[1],
                'username': row[2],
                'hashed_password': row[3],
                'full_name': row[4],
                'is_active': row[5],
                'is_verified': row[6],
                'is_superuser': row[7],
                'created_at': row[8],
                'last_login': row[9]
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching user by username: {e}")
        raise
    finally:
        conn.close()


def create_user(email: str, username: str, password: str, full_name: Optional[str] = None) -> dict:
   
    # Check if user already exists
    if get_user_by_email(email):
        raise ValueError("Email already registered")

    if get_user_by_username(username):
        raise ValueError("Username already taken")

    # Hash password
    hashed_password = get_password_hash(password)

    # Generate verification token
    verification_token = generate_verification_token()
    verification_token_expires = datetime.utcnow() + timedelta(hours=24)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (email, username, hashed_password, full_name,
                             verification_token, verification_token_expires)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, email, username, full_name, is_active, is_verified,
                      is_superuser, created_at, verification_token
            """,
            (email, username, hashed_password, full_name, verification_token, verification_token_expires)
        )
        row = cursor.fetchone()
        conn.commit()
        cursor.close()

        logger.info(f"User created successfully: {email}")

        return {
            'id': row[0],
            'email': row[1],
            'username': row[2],
            'full_name': row[3],
            'is_active': row[4],
            'is_verified': row[5],
            'is_superuser': row[6],
            'created_at': row[7],
            'verification_token': row[8]
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating user: {e}")
        raise
    finally:
        conn.close()


def verify_user_email(verification_token: str) -> bool:
   
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Check if token exists and is not expired
        cursor.execute(
            """
            UPDATE users
            SET is_verified = TRUE,
                verification_token = NULL,
                verification_token_expires = NULL
            WHERE verification_token = %s
              AND verification_token_expires > NOW()
              AND is_verified = FALSE
            RETURNING id
            """,
            (verification_token,)
        )

        result = cursor.fetchone()
        conn.commit()
        cursor.close()

        if result:
            logger.info(f"Email verified for user ID: {result[0]}")
            return True

        logger.warning(f"Invalid or expired verification token")
        return False

    except Exception as e:
        conn.rollback()
        logger.error(f"Error verifying email: {e}")
        raise
    finally:
        conn.close()


def update_last_login(email: str):
    """
    Update the last login timestamp for a user.

    Args:
        email: User's email address
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET last_login = NOW()
            WHERE email = %s
            """,
            (email,)
        )
        conn.commit()
        cursor.close()
        logger.info(f"Updated last login for: {email}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating last login: {e}")
        raise
    finally:
        conn.close()
