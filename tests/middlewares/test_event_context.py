"""Tests for app/middlewares/event_context.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.middlewares.event_context import EventContextMiddleware
from tests.conftest import make_bot, make_chat, make_message, make_update, make_user


class TestEventContextMiddleware:
    @pytest.fixture
    def middleware(self):
        return EventContextMiddleware()

    @pytest.fixture
    def handler(self):
        return AsyncMock(return_value="handler_result")

    @pytest.mark.asyncio
    async def test_adds_bot_to_data(self, middleware, handler):
        bot = make_bot()
        msg = make_message()
        update = make_update(message=msg)
        update.bot = bot
        data = {}

        await middleware(handler, update, data)

        assert data["bot"] == bot
        handler.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_adds_user_to_data(self, middleware, handler):
        user = make_user(id=123, first_name="TestUser")
        msg = make_message(from_user=user)
        update = make_update(message=msg)
        data = {}

        await middleware(handler, update, data)

        assert data["user"] == user

    @pytest.mark.asyncio
    async def test_adds_chat_to_data(self, middleware, handler):
        chat = make_chat(id=-100123, title="Test Chat")
        msg = make_message(chat=chat)
        update = make_update(message=msg)
        data = {}

        await middleware(handler, update, data)

        assert data["chat"] == chat

    @pytest.mark.asyncio
    async def test_raises_on_non_update_event(self, middleware, handler):
        non_update_event = MagicMock()

        with pytest.raises(RuntimeError, match="unexpected event type"):
            await middleware(handler, non_update_event, {})

    @pytest.mark.asyncio
    async def test_returns_handler_result(self, middleware, handler):
        msg = make_message()
        update = make_update(message=msg)

        result = await middleware(handler, update, {})

        assert result == "handler_result"
