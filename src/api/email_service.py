"""
Email service for sending verification emails via SendGrid.
"""
import logging
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content

from src.config.settings import EmailConfig

logger = logging.getLogger(__name__)


def send_verification_email(email: str, verification_token: str, username: str) -> bool:
    """
    Send email verification link to user via SendGrid.

    Args:
        email: User's email address
        verification_token: Verification token
        username: User's username

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    logger.info(f"send_verification_email called for {email}")
    logger.info(f"EMAIL_ENABLED: {EmailConfig.EMAIL_ENABLED}")
    logger.info(f"SENDGRID_API_KEY present: {bool(EmailConfig.SENDGRID_API_KEY)}")

    if not EmailConfig.EMAIL_ENABLED:
        logger.info(f"Email sending disabled. Verification token for {email}: {verification_token}")
        return False

    try:
        logger.info(f"Attempting to send email to {email}")
        # Build verification URL
        verification_url = f"{EmailConfig.EMAIL_VERIFICATION_URL}?verification_token={verification_token}"

        # Email subject and body
        subject = "Verify Your Email - Sales Analytics"
        html_body = _build_verification_email_html(username, verification_url)
        text_body = _build_verification_email_text(username, verification_url)

        # Create SendGrid message
        message = Mail(
            from_email=(EmailConfig.EMAIL_FROM, EmailConfig.EMAIL_FROM_NAME),
            to_emails=email,
            subject=subject,
            plain_text_content=Content("text/plain", text_body),
            html_content=Content("text/html", html_body)
        )

        # Send via SendGrid API
        sg = SendGridAPIClient(EmailConfig.SENDGRID_API_KEY)
        response = sg.send(message)

        logger.info(f"SendGrid response: Status {response.status_code}")

        if response.status_code in [200, 201, 202]:
            logger.info(f"Verification email sent via SendGrid to {email}")
            return True
        else:
            logger.error(f"SendGrid returned status code: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")
        logger.exception("Full exception details:")
        return False


def _build_verification_email_html(username: str, verification_url: str) -> str:
    """Build HTML email body for verification."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Sales Analytics</h1>
        </div>
        <div class="content">
            <h2>Welcome, {username}!</h2>
            <p>Thank you for registering with Sales Analytics. Please verify your email address to activate your account.</p>

            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>

            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background-color: #e9e9e9; padding: 10px; border-radius: 3px;">
                {verification_url}
            </p>

            <p><strong>Note:</strong> This verification link will expire in 24 hours.</p>

            <p>If you didn't create an account with Sales Analytics, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Sales Analytics. All rights reserved.</p>
        </div>
    </body>
    </html>
    """


def _build_verification_email_text(username: str, verification_url: str) -> str:
    """Build plain text email body for verification."""
    return f"""
Welcome to Sales Analytics, {username}!

Thank you for registering. Please verify your email address to activate your account.

Verification Link:
{verification_url}

This verification link will expire in 24 hours.

If you didn't create an account with Sales Analytics, please ignore this email.

---
Sales Analytics
© 2025 All rights reserved.
"""


def send_password_reset_email(email: str, reset_token: str) -> bool:
    """
    Send password reset email to user.

    Args:
        email: User's email address
        reset_token: Password reset token

    Returns:
        bool: True if email sent successfully

    Note: This is a placeholder for future password reset functionality.
    """
    logger.info(f"Password reset email requested for {email} (not implemented)")
    return False
