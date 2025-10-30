"""Tests for skip_anonymous middleware."""

import pytest

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

from aiogram.dispatcher.event.bases import UNHANDLED
from middlewares.skip_anonymous import SkipAnonymousMessagesMiddleware


@pytest.fixture
def middleware():
    """Create middleware instance for testing."""
    return SkipAnonymousMessagesMiddleware()


@pytest.fixture
def mock_message():
    """Create mock Telegram message."""
    message = Mock()
    message.from_user = Mock()
    message.chat = Mock()
    message.chat.id = 123456
    message.sender_chat = None
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_handler():
    """Create mock handler."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_skip_auto_forwards(middleware, mock_message, mock_handler):
    """Test that auto-forwards from channels are skipped."""
    mock_message.from_user.id = 777000  # Telegram channel ID

    result = await middleware(mock_handler, mock_message, {})

    # Handler should not be called
    mock_handler.assert_not_called()

    # Should return UNHANDLED
    assert result is UNHANDLED


@pytest.mark.asyncio
async def test_reply_to_anonymous_sender(middleware, mock_message, mock_handler):
    """Test that anonymous messages get a reply."""
    mock_message.from_user.id = 1087968824  # Anonymous admin ID
    mock_message.sender_chat = Mock()  # Has sender_chat = anonymous

    result = await middleware(mock_handler, mock_message, {})

    # Should reply to message
    mock_message.reply.assert_called_once()
    assert "анонимами" in str(mock_message.reply.call_args)

    # Handler should not be called
    mock_handler.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_anonymous_replies(middleware, mock_message, mock_handler):
    """Test that replies to anonymous messages are rate-limited."""
    mock_message.from_user.id = 1087968824
    mock_message.sender_chat = Mock()

    # First call should reply
    await middleware(mock_handler, mock_message, {})
    assert mock_message.reply.call_count == 1

    # Second call within interval should not reply
    await middleware(mock_handler, mock_message, {})
    assert mock_message.reply.call_count == 1  # Still 1, not 2

    # Simulate time passing
    middleware.last_reply_dt[mock_message.chat.id] = datetime.utcnow() - timedelta(
        hours=2
    )

    # Third call after interval should reply
    await middleware(mock_handler, mock_message, {})
    assert mock_message.reply.call_count == 2


@pytest.mark.asyncio
async def test_allow_normal_messages(middleware, mock_message, mock_handler):
    """Test that normal user messages are allowed through."""
    mock_message.from_user.id = 123456  # Normal user ID
    mock_message.sender_chat = None

    result = await middleware(mock_handler, mock_message, {})

    # Handler should be called
    mock_handler.assert_called_once_with(mock_message, {})

    # Should return handler result
    assert result == mock_handler.return_value
