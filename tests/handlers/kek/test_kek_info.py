"""Tests for app/handlers/kek/kek_info.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import make_message


class TestCmdKekInfo:
    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.async_all = AsyncMock(
            return_value=[
                {
                    "id": "rec1",
                    "fields": {
                        "Text": "Kek 1",
                        "AttachmentType": "text",
                    },
                },
                {
                    "id": "rec2",
                    "fields": {
                        "Text": "Kek 2",
                        "AttachmentType": "photo",
                    },
                },
                {
                    "id": "rec3",
                    "fields": {
                        "Text": "Kek 3",
                        "AttachmentType": "text",
                    },
                },
            ]
        )
        storage.async_all_users = AsyncMock(
            return_value=[
                {
                    "id": "user1",
                    "fields": {
                        "Name": "User One",
                        "TelegramID": 123,
                        "Author": ["rec1", "rec2"],
                        "Suggestor": [],
                    },
                },
                {
                    "id": "user2",
                    "fields": {
                        "Name": "User Two",
                        "TelegramID": 456,
                        "Author": ["rec3"],
                        "Suggestor": ["rec1", "rec2", "rec3"],
                    },
                },
            ]
        )
        return storage

    @pytest.mark.asyncio
    async def test_fetches_keks_and_users(self, mock_storage):
        msg = make_message()

        with patch("handlers.kek.kek_info.kek_storage", mock_storage):
            from handlers.kek.kek_info import cmd_kek_info

            await cmd_kek_info(msg)

        mock_storage.async_all.assert_awaited_once()
        mock_storage.async_all_users.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_replies_with_statistics(self, mock_storage):
        msg = make_message()

        with patch("handlers.kek.kek_info.kek_storage", mock_storage):
            from handlers.kek.kek_info import cmd_kek_info

            await cmd_kek_info(msg)

        msg.reply.assert_awaited_once()
        call_kwargs = msg.reply.call_args.kwargs
        assert "text" in call_kwargs

    @pytest.mark.asyncio
    async def test_shows_total_kek_count(self, mock_storage):
        msg = make_message()

        with patch("handlers.kek.kek_info.kek_storage", mock_storage):
            from handlers.kek.kek_info import cmd_kek_info

            await cmd_kek_info(msg)

        call_kwargs = msg.reply.call_args.kwargs
        # 3 keks in mock data
        assert "3" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_shows_attachment_types(self, mock_storage):
        msg = make_message()

        with patch("handlers.kek.kek_info.kek_storage", mock_storage):
            from handlers.kek.kek_info import cmd_kek_info

            await cmd_kek_info(msg)

        call_kwargs = msg.reply.call_args.kwargs
        # Should show text and photo types
        assert "text" in call_kwargs["text"]
        assert "photo" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_shows_top_authors(self, mock_storage):
        msg = make_message()

        with patch("handlers.kek.kek_info.kek_storage", mock_storage):
            from handlers.kek.kek_info import cmd_kek_info

            await cmd_kek_info(msg)

        call_kwargs = msg.reply.call_args.kwargs
        # User One has 2 authored keks
        assert "User One" in call_kwargs["text"]
        assert "2" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_disables_notification(self, mock_storage):
        msg = make_message()

        with patch("handlers.kek.kek_info.kek_storage", mock_storage):
            from handlers.kek.kek_info import cmd_kek_info

            await cmd_kek_info(msg)

        call_kwargs = msg.reply.call_args.kwargs
        assert call_kwargs.get("disable_notification") is True
