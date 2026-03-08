"""Notification delivery module for Telegram and email channels.

Sends portfolio summaries via configured channels. Channel availability
is auto-detected from environment variables.
"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx


def send_telegram(message: str) -> bool:
    """Send a message via Telegram Bot API.

    Reads CRYPTO_TELEGRAM_TOKEN and CRYPTO_TELEGRAM_CHAT_ID from environment.
    Returns True on success, False if not configured.
    Raises httpx.HTTPStatusError on HTTP errors.
    """
    token = os.environ.get("CRYPTO_TELEGRAM_TOKEN")
    chat_id = os.environ.get("CRYPTO_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = httpx.post(url, json={
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    })
    response.raise_for_status()
    return True


def send_email(subject: str, html_body: str, text_body: str) -> bool:
    """Send an HTML email via SMTP with STARTTLS.

    Reads CRYPTO_SMTP_* environment variables.
    Returns True on success, False if not configured.
    """
    host = os.environ.get("CRYPTO_SMTP_HOST")
    if not host:
        return False
    port = int(os.environ.get("CRYPTO_SMTP_PORT", "587"))
    user = os.environ.get("CRYPTO_SMTP_USER", "")
    password = os.environ.get("CRYPTO_SMTP_PASS", "")
    from_addr = os.environ.get("CRYPTO_SMTP_FROM", "")
    to_addr = os.environ.get("CRYPTO_SMTP_TO", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        if user and password:
            server.login(user, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
    return True


def send_summary(text_message: str, html_message: str) -> list[str]:
    """Send summary to all configured channels.

    Catches errors per channel so one failure does not block others.
    Returns list of channel names that succeeded.
    """
    sent: list[str] = []

    try:
        if send_telegram(text_message):
            sent.append("telegram")
    except Exception as e:
        print(f"Telegram send failed: {e}")

    try:
        if send_email("Crypto Portfolio Summary", html_message, text_message):
            sent.append("email")
    except Exception as e:
        print(f"Email send failed: {e}")

    return sent
