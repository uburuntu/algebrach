"""Tests for kek handler."""

import pytest

from unittest.mock import AsyncMock, Mock, patch

from handlers.kek.kek import cmd_kek


@pytest.mark.asyncio
async def test_cmd_kek_returns_kek_when_available():
    """Test that cmd_kek returns a kek when keks are available."""
    # Mock message
    mock_message = AsyncMock()
    mock_message.reply = AsyncMock()

    # Mock storage response
    mock_keks = [
        {
            "id": "rec123",
            "fields": {
                "Text": "Test kek",
                "AttachmentType": None,
                "AttachmentFileID": None,
                "Attachment": None,
            },
        }
    ]

    with patch("handlers.kek.kek.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(return_value=mock_keks)
        with patch("handlers.kek.kek.reply_with_attachment") as mock_reply:
            mock_reply.return_value = Mock()

            result = await cmd_kek(mock_message)

            # Verify storage was called
            mock_storage.async_all.assert_called_once()

            # Verify reply was called with correct parameters
            mock_reply.assert_called_once()
            assert result is not None


@pytest.mark.asyncio
async def test_cmd_kek_handles_empty_keks_list():
    """Test that cmd_kek handles empty keks list gracefully."""
    mock_message = AsyncMock()
    mock_message.reply = AsyncMock()

    with patch("handlers.kek.kek.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(return_value=[])

        result = await cmd_kek(mock_message)

        # Verify error message was sent
        mock_message.reply.assert_called_once()
        assert "No keks available" in str(mock_message.reply.call_args)
        assert result is None


@pytest.mark.asyncio
async def test_cmd_kek_handles_timeout_error():
    """Test that cmd_kek handles TimeoutError gracefully."""
    mock_message = AsyncMock()
    mock_message.reply = AsyncMock()

    with patch("handlers.kek.kek.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(side_effect=TimeoutError())

        result = await cmd_kek(mock_message)

        # Verify timeout error message was sent
        mock_message.reply.assert_called_once()
        assert "temporarily slow" in str(mock_message.reply.call_args)
        assert result is None


@pytest.mark.asyncio
async def test_cmd_kek_handles_unexpected_error():
    """Test that cmd_kek handles unexpected errors gracefully."""
    mock_message = AsyncMock()
    mock_message.reply = AsyncMock()

    with patch("handlers.kek.kek.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(side_effect=Exception("Database error"))

        result = await cmd_kek(mock_message)

        # Verify generic error message was sent
        mock_message.reply.assert_called_once()
        assert "unexpected error" in str(mock_message.reply.call_args)
        assert result is None


@pytest.mark.asyncio
async def test_cmd_kek_with_attachment():
    """Test that cmd_kek handles keks with attachments correctly."""
    mock_message = AsyncMock()

    mock_keks = [
        {
            "id": "rec456",
            "fields": {
                "Text": "Kek with photo",
                "AttachmentType": "photo",
                "AttachmentFileID": "AgACAgIAAxkBAAI...",
                "Attachment": [{"url": "https://example.com/photo.jpg"}],
            },
        }
    ]

    with patch("handlers.kek.kek.kek_storage") as mock_storage:
        mock_storage.async_all = AsyncMock(return_value=mock_keks)
        with patch("handlers.kek.kek.reply_with_attachment") as mock_reply:
            mock_reply.return_value = Mock()
            with patch("handlers.kek.kek.config") as mock_config:
                mock_config.environment = "test"

                result = await cmd_kek(mock_message)

                # Verify reply_with_attachment was called with correct params
                mock_reply.assert_called_once()
                call_args = mock_reply.call_args
                assert call_args[0][1] == "Kek with photo"  # text
                assert call_args[0][2] == "photo"  # attachment_type
                assert result is not None
