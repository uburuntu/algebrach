"""Tests for app/middlewares/skip_anonymous.py"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from aiogram.dispatcher.event.bases import UNHANDLED

from app.middlewares.skip_anonymous import SkipAnonymousMessagesMiddleware
from tests.conftest import make_chat, make_message, make_user


class TestSkipAnonymousMessagesMiddleware:
    @pytest.fixture
    def middleware(self):
        return SkipAnonymousMessagesMiddleware()

    @pytest.fixture
    def handler(self):
        return AsyncMock(return_value="result")

    @pytest.mark.asyncio
    async def test_normal_user_passes_through(self, middleware, handler):
        user = make_user(id=12345, first_name="Regular")
        msg = make_message(from_user=user)

        result = await middleware(handler, msg, {})

        handler.assert_awaited_once_with(msg, {})
        assert result == "result"

    @pytest.mark.asyncio
    async def test_auto_forward_user_skipped(self, middleware, handler):
        # Auto-forward user ID from channels
        user = make_user(id=777000, first_name="Telegram")
        msg = make_message(from_user=user)

        result = await middleware(handler, msg, {})

        handler.assert_not_awaited()
        assert result is UNHANDLED

    @pytest.mark.asyncio
    async def test_sender_chat_replies_once_per_interval(self, middleware, handler):
        user = make_user(id=1234, first_name="User")
        chat = make_chat(id=-100999)
        sender_chat = make_chat(id=-100888, type="channel", title="Channel")
        msg = make_message(from_user=user, chat=chat, sender_chat=sender_chat)

        # First message with sender_chat should reply
        await middleware(handler, msg, {})

        msg.reply.assert_awaited_once()
        handler.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_sender_chat_no_reply_within_interval(self, middleware, handler):
        user = make_user(id=1234, first_name="User")
        chat = make_chat(id=-100999)
        sender_chat = make_chat(id=-100888, type="channel", title="Channel")
        msg = make_message(from_user=user, chat=chat, sender_chat=sender_chat)

        # Simulate recent reply
        middleware.last_reply_dt[chat.id] = datetime.now(UTC)

        await middleware(handler, msg, {})

        # Should not reply again
        msg.reply.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_sender_chat_replies_after_interval(self, middleware, handler):
        user = make_user(id=1234, first_name="User")
        chat = make_chat(id=-100999)
        sender_chat = make_chat(id=-100888, type="channel", title="Channel")
        msg = make_message(from_user=user, chat=chat, sender_chat=sender_chat)

        # Simulate reply that happened 2 hours ago
        middleware.last_reply_dt[chat.id] = datetime.now(UTC) - timedelta(hours=2)

        await middleware(handler, msg, {})

        # Should reply again after interval passed
        msg.reply.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_anonymous_sender_id_triggers_reply(self, middleware, handler):
        # Anonymous admin user ID
        user = make_user(id=1087968824, first_name="Anonymous")
        chat = make_chat(id=-100999)
        sender_chat = make_chat(id=-100999, type="supergroup", title="Group")
        msg = make_message(from_user=user, chat=chat, sender_chat=sender_chat)

        await middleware(handler, msg, {})

        msg.reply.assert_awaited_once()
        handler.assert_not_awaited()
