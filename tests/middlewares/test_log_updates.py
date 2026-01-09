"""Tests for app/middlewares/log_updates.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from aiogram.dispatcher.event.bases import UNHANDLED

from app.middlewares.log_updates import LogUpdatesMiddleware

from tests.conftest import make_chat, make_message, make_update, make_user


class TestLogUpdatesMiddleware:
    @pytest.fixture
    def middleware(self):
        return LogUpdatesMiddleware()

    @pytest.fixture
    def handler(self):
        return AsyncMock(return_value="result")

    @pytest.mark.asyncio
    async def test_logs_handled_update(self, middleware, handler, mocker):
        spy = mocker.spy(middleware.logger, "info")

        msg = make_message(text="Hello world")
        update = make_update(message=msg)

        await middleware(handler, update, {})

        spy.assert_called_once()
        log_message = spy.call_args[0][0]
        assert "Message" in log_message
        assert "Hello world" in log_message

    @pytest.mark.asyncio
    async def test_logs_unhandled_update_as_debug(self, middleware, mocker):
        handler = AsyncMock(return_value=UNHANDLED)
        spy = mocker.spy(middleware.logger, "debug")

        msg = make_message(text="Ignored")
        update = make_update(message=msg)

        await middleware(handler, update, {})

        spy.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_on_non_update_event(self, middleware, handler):
        non_update = MagicMock()

        with pytest.raises(RuntimeError, match="unexpected event type"):
            await middleware(handler, non_update, {})

    def test_log_string_format_with_user_and_chat(self):
        user = make_user(id=123, first_name="John", username="john")
        chat = make_chat(id=-100123, type="supergroup", title="Test Group")
        msg = make_message(
            message_id=42, from_user=user, chat=chat, text="Test message"
        )
        update = make_update(message=msg)

        log = LogUpdatesMiddleware.log_string(update, elapsed_ms=150)

        assert "Message" in log
        assert "150 ms" in log
        assert "Test Group" in log
        assert "John" in log
        assert "Test message" in log

    def test_log_string_format_private_chat(self):
        user = make_user(id=123, first_name="Alice")
        chat = make_chat(id=123, type="private", title=None)
        msg = make_message(message_id=1, from_user=user, chat=chat, text="Private msg")
        update = make_update(message=msg)

        log = LogUpdatesMiddleware.log_string(update, elapsed_ms=50)

        assert "private" in log
        assert "Alice" in log

    def test_log_string_with_edited_message(self):
        msg = make_message(text="Edited text")
        update = make_update(edited_message=msg)

        log = LogUpdatesMiddleware.log_string(update, elapsed_ms=100)

        assert "[edited]" in log

