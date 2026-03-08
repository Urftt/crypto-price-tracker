"""Unit tests for the notification module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from crypto_price_tracker.notify import send_email, send_summary, send_telegram


# ---------------------------------------------------------------------------
# send_telegram tests
# ---------------------------------------------------------------------------

def test_send_telegram_success(monkeypatch):
    """With env vars set and HTTP 200, send_telegram returns True."""
    monkeypatch.setenv("CRYPTO_TELEGRAM_TOKEN", "fake-token")
    monkeypatch.setenv("CRYPTO_TELEGRAM_CHAT_ID", "12345")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()

    with patch("crypto_price_tracker.notify.httpx.post", return_value=mock_response) as mock_post:
        result = send_telegram("<b>Test message</b>")

    assert result is True
    mock_post.assert_called_once_with(
        "https://api.telegram.org/botfake-token/sendMessage",
        json={
            "chat_id": "12345",
            "text": "<b>Test message</b>",
            "parse_mode": "HTML",
        },
    )


def test_send_telegram_not_configured(monkeypatch):
    """Without env vars, send_telegram returns False without making HTTP calls."""
    monkeypatch.delenv("CRYPTO_TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("CRYPTO_TELEGRAM_CHAT_ID", raising=False)

    with patch("crypto_price_tracker.notify.httpx.post") as mock_post:
        result = send_telegram("test")

    assert result is False
    mock_post.assert_not_called()


def test_send_telegram_missing_token(monkeypatch):
    """With only chat_id set, returns False."""
    monkeypatch.delenv("CRYPTO_TELEGRAM_TOKEN", raising=False)
    monkeypatch.setenv("CRYPTO_TELEGRAM_CHAT_ID", "12345")

    result = send_telegram("test")
    assert result is False


def test_send_telegram_missing_chat_id(monkeypatch):
    """With only token set, returns False."""
    monkeypatch.setenv("CRYPTO_TELEGRAM_TOKEN", "fake-token")
    monkeypatch.delenv("CRYPTO_TELEGRAM_CHAT_ID", raising=False)

    result = send_telegram("test")
    assert result is False


def test_send_telegram_http_error(monkeypatch):
    """HTTP errors propagate to caller."""
    monkeypatch.setenv("CRYPTO_TELEGRAM_TOKEN", "fake-token")
    monkeypatch.setenv("CRYPTO_TELEGRAM_CHAT_ID", "12345")

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=MagicMock()
    )

    with patch("crypto_price_tracker.notify.httpx.post", return_value=mock_response):
        with pytest.raises(httpx.HTTPStatusError):
            send_telegram("test")


# ---------------------------------------------------------------------------
# send_email tests
# ---------------------------------------------------------------------------

def test_send_email_success(monkeypatch):
    """With all SMTP env vars, send_email returns True."""
    monkeypatch.setenv("CRYPTO_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("CRYPTO_SMTP_PORT", "587")
    monkeypatch.setenv("CRYPTO_SMTP_USER", "user@example.com")
    monkeypatch.setenv("CRYPTO_SMTP_PASS", "secret")
    monkeypatch.setenv("CRYPTO_SMTP_FROM", "from@example.com")
    monkeypatch.setenv("CRYPTO_SMTP_TO", "to@example.com")

    mock_server = MagicMock()
    mock_server.__enter__ = MagicMock(return_value=mock_server)
    mock_server.__exit__ = MagicMock(return_value=False)

    with patch("crypto_price_tracker.notify.smtplib.SMTP", return_value=mock_server):
        result = send_email("Test Subject", "<html>body</html>", "plain body")

    assert result is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@example.com", "secret")
    mock_server.sendmail.assert_called_once()


def test_send_email_not_configured(monkeypatch):
    """Without SMTP host, returns False."""
    monkeypatch.delenv("CRYPTO_SMTP_HOST", raising=False)

    result = send_email("Subject", "<html></html>", "text")
    assert result is False


def test_send_email_no_login_when_no_credentials(monkeypatch):
    """With host but no user/password, skips login but sends mail."""
    monkeypatch.setenv("CRYPTO_SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("CRYPTO_SMTP_PORT", "587")
    monkeypatch.delenv("CRYPTO_SMTP_USER", raising=False)
    monkeypatch.delenv("CRYPTO_SMTP_PASS", raising=False)
    monkeypatch.setenv("CRYPTO_SMTP_FROM", "from@example.com")
    monkeypatch.setenv("CRYPTO_SMTP_TO", "to@example.com")

    mock_server = MagicMock()
    mock_server.__enter__ = MagicMock(return_value=mock_server)
    mock_server.__exit__ = MagicMock(return_value=False)

    with patch("crypto_price_tracker.notify.smtplib.SMTP", return_value=mock_server):
        result = send_email("Subject", "<html>body</html>", "text")

    assert result is True
    mock_server.login.assert_not_called()
    mock_server.sendmail.assert_called_once()


# ---------------------------------------------------------------------------
# send_summary tests
# ---------------------------------------------------------------------------

def test_send_summary_both_channels():
    """When both channels succeed, returns both names."""
    with (
        patch("crypto_price_tracker.notify.send_telegram", return_value=True),
        patch("crypto_price_tracker.notify.send_email", return_value=True),
    ):
        result = send_summary("text msg", "<html>html msg</html>")

    assert result == ["telegram", "email"]


def test_send_summary_telegram_only():
    """When only telegram succeeds, returns ['telegram']."""
    with (
        patch("crypto_price_tracker.notify.send_telegram", return_value=True),
        patch("crypto_price_tracker.notify.send_email", return_value=False),
    ):
        result = send_summary("text", "html")

    assert result == ["telegram"]


def test_send_summary_no_channels():
    """When no channels configured, returns empty list."""
    with (
        patch("crypto_price_tracker.notify.send_telegram", return_value=False),
        patch("crypto_price_tracker.notify.send_email", return_value=False),
    ):
        result = send_summary("text", "html")

    assert result == []


def test_send_summary_telegram_error_continues():
    """When telegram raises, email should still be tried."""
    with (
        patch("crypto_price_tracker.notify.send_telegram", side_effect=RuntimeError("boom")),
        patch("crypto_price_tracker.notify.send_email", return_value=True),
    ):
        result = send_summary("text", "html")

    assert result == ["email"]
