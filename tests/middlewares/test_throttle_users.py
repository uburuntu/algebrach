"""Tests for app/middlewares/throttle_users.py"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from aiogram.dispatcher.event.bases import UNHANDLED

from app.middlewares.throttle_users import ThrottleUsersMiddleware

from tests.conftest import make_message, make_user


class TestThrottleUsersMiddleware:
    @pytest.fixture
    def middleware(self):
        return ThrottleUsersMiddleware()

    @pytest.mark.asyncio
    async def test_allows_first_message(self, middleware):
        handler = AsyncMock(return_value="result")
        user = make_user(id=123)
        msg = make_message(from_user=user)

        result = await middleware(handler, msg, {})

        handler.assert_awaited_once_with(msg, {})
        assert result == "result"

    @pytest.mark.asyncio
    async def test_clears_user_after_handler_completes(self, middleware):
        handler = AsyncMock(return_value="result")
        user = make_user(id=123)
        msg = make_message(from_user=user)

        # First call
        await middleware(handler, msg, {})
        assert user.id not in middleware.active_users

        # Second call should also work
        handler.reset_mock()
        await middleware(handler, msg, {})
        handler.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_blocks_concurrent_messages_from_same_user(self, middleware):
        # Slow handler simulating processing
        async def slow_handler(event, data):
            await asyncio.sleep(0.2)
            return "slow_result"

        handler = AsyncMock(side_effect=slow_handler)
        user = make_user(id=456)
        msg = make_message(from_user=user)

        async def first_request():
            return await middleware(handler, msg, {})

        async def second_request():
            await asyncio.sleep(0.05)  # Start slightly after
            return await middleware(handler, msg, {})

        results = await asyncio.gather(first_request(), second_request())

        # First should complete, second should be skipped
        assert results[0] == "slow_result"
        assert results[1] is UNHANDLED
        handler.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_allows_concurrent_messages_from_different_users(self, middleware):
        call_count = 0

        async def counting_handler(event, data):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            return "result"

        handler = AsyncMock(side_effect=counting_handler)

        user1 = make_user(id=111)
        user2 = make_user(id=222)
        msg1 = make_message(from_user=user1)
        msg2 = make_message(from_user=user2)

        results = await asyncio.gather(
            middleware(handler, msg1, {}), middleware(handler, msg2, {})
        )

        # Both should complete
        assert results == ["result", "result"]
        assert handler.await_count == 2

    @pytest.mark.asyncio
    async def test_clears_user_even_on_exception(self, middleware):
        handler = AsyncMock(side_effect=ValueError("Test error"))
        user = make_user(id=789)
        msg = make_message(from_user=user)

        with pytest.raises(ValueError):
            await middleware(handler, msg, {})

        # User should be cleared from active set
        assert user.id not in middleware.active_users

