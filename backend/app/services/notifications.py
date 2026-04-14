"""Notification service stubs."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def send_email_notification(
    to_email: str,
    subject: str,
    body: str,
) -> bool:
    """Send an email notification (stub)."""
    logger.info(f"[STUB] Email notification to {to_email}: {subject}")
    return True


async def send_telegram_notification(
    chat_id: str,
    message: str,
) -> bool:
    """Send a Telegram notification (stub)."""
    logger.info(f"[STUB] Telegram notification to {chat_id}: {message}")
    return True


async def send_web_push_notification(
    user_id: str,
    title: str,
    body: str,
    url: Optional[str] = None,
) -> bool:
    """Send a web push notification (stub)."""
    logger.info(f"[STUB] Web push notification to user {user_id}: {title}")
    return True
