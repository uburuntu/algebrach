"""Tests for app/handlers/kek/kek.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import make_message


class TestCmdKek:
    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.async_all = AsyncMock(
            return_value=[
                {
                    "id": "rec123",
                    "fields": {
                        "Text": "Test kek text",
                        "AttachmentType": None,
                        "AttachmentFileID": None,
                        "Attachment": None,
                    },
                }
            ]
        )
        storage.async_update_file_id = AsyncMock()
        return storage

    @pytest.mark.asyncio
    async def test_replies_with_random_kek(self, mock_storage):
        msg = make_message()

        with patch("handlers.kek.kek.kek_storage", mock_storage):
            from handlers.kek.kek import cmd_kek

            await cmd_kek(msg)

        mock_storage.async_all.assert_awaited_once()
        msg.reply.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_text_only_kek(self, mock_storage):
        mock_storage.async_all = AsyncMock(
            return_value=[
                {
                    "id": "rec1",
                    "fields": {
                        "Text": "Pure text kek",
                        "AttachmentType": None,
                        "AttachmentFileID": None,
                        "Attachment": None,
                    },
                }
            ]
        )
        msg = make_message()

        with patch("handlers.kek.kek.kek_storage", mock_storage):
            from handlers.kek.kek import cmd_kek

            await cmd_kek(msg)

        msg.reply.assert_awaited_once_with(
            "Pure text kek", disable_web_page_preview=False
        )

    @pytest.mark.asyncio
    async def test_kek_with_photo(self, mock_storage):
        mock_storage.async_all = AsyncMock(
            return_value=[
                {
                    "id": "rec2",
                    "fields": {
                        "Text": "Photo caption",
                        "AttachmentType": "photo",
                        "AttachmentFileID": "photo_id_123",
                        "Attachment": [{"url": "https://example.com/photo.jpg"}],
                    },
                }
            ]
        )
        msg = make_message()

        with patch("handlers.kek.kek.kek_storage", mock_storage):
            from handlers.kek.kek import cmd_kek

            await cmd_kek(msg)

        msg.reply_photo.assert_awaited_once_with("photo_id_123", caption="Photo caption")

    @pytest.mark.asyncio
    async def test_updates_file_id_in_prod(self, mock_storage):
        mock_storage.async_all = AsyncMock(
            return_value=[
                {
                    "id": "rec3",
                    "fields": {
                        "Text": "Photo kek",
                        "AttachmentType": "photo",
                        "AttachmentFileID": "old_photo_id",
                        "Attachment": [{"url": "https://example.com/photo.jpg"}],
                    },
                }
            ]
        )

        # Make reply return message with different file_id
        reply_msg = make_message()
        from unittest.mock import MagicMock
        from aiogram.types import PhotoSize

        photo = MagicMock(spec=PhotoSize)
        photo.file_id = "new_photo_id"
        reply_msg.photo = [photo]

        msg = make_message()
        msg.reply_photo = AsyncMock(return_value=reply_msg)

        with (
            patch("handlers.kek.kek.kek_storage", mock_storage),
            patch("handlers.kek.kek.config") as mock_config,
        ):
            mock_config.environment = "prod"

            from handlers.kek.kek import cmd_kek

            await cmd_kek(msg)

        mock_storage.async_update_file_id.assert_awaited_once_with(
            "rec3", "new_photo_id"
        )

    @pytest.mark.asyncio
    async def test_no_file_id_update_in_dev(self, mock_storage):
        mock_storage.async_all = AsyncMock(
            return_value=[
                {
                    "id": "rec3",
                    "fields": {
                        "Text": "Photo kek",
                        "AttachmentType": "photo",
                        "AttachmentFileID": "old_photo_id",
                        "Attachment": [{"url": "https://example.com/photo.jpg"}],
                    },
                }
            ]
        )
        msg = make_message()

        with (
            patch("handlers.kek.kek.kek_storage", mock_storage),
            patch("handlers.kek.kek.config") as mock_config,
        ):
            mock_config.environment = "dev"

            from handlers.kek.kek import cmd_kek

            await cmd_kek(msg)

        mock_storage.async_update_file_id.assert_not_awaited()

