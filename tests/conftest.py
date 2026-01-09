"""
Reusable test fixtures for the algebrach test suite.

Provides mock factories for aiogram types (User, Chat, Message, Bot)
and other common test dependencies.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiogram.types import Chat, Message, PhotoSize, Update, User


# =============================================================================
# User Fixtures
# =============================================================================


def make_user(
    id: int = 123456,
    is_bot: bool = False,
    first_name: str = "TestUser",
    last_name: str | None = None,
    username: str | None = None,
    language_code: str | None = "en",
) -> User:
    """Factory to create User objects with sensible defaults."""
    return User(
        id=id,
        is_bot=is_bot,
        first_name=first_name,
        last_name=last_name,
        username=username,
        language_code=language_code,
    )


@pytest.fixture
def user() -> User:
    """Default test user."""
    return make_user()


@pytest.fixture
def admin_user() -> User:
    """Admin user (id matches config.admin_ids)."""
    return make_user(id=28006241, first_name="Admin", username="admin")


@pytest.fixture
def anonymous_user() -> User:
    """Anonymous sender user (id=1087968824)."""
    return make_user(id=1087968824, first_name="Anonymous")


@pytest.fixture
def auto_forward_user() -> User:
    """Auto-forward user (id=777000)."""
    return make_user(id=777000, first_name="Telegram")


# =============================================================================
# Chat Fixtures
# =============================================================================


def make_chat(
    id: int = -1001234567890,
    type: str = "supergroup",
    title: str | None = "Test Chat",
    username: str | None = None,
) -> Chat:
    """Factory to create Chat objects with sensible defaults."""
    return Chat(
        id=id,
        type=type,
        title=title,
        username=username,
    )


@pytest.fixture
def chat() -> Chat:
    """Default test supergroup chat."""
    return make_chat()


@pytest.fixture
def private_chat() -> Chat:
    """Private chat."""
    return make_chat(id=123456, type="private", title=None)


@pytest.fixture
def mechmath_chat() -> Chat:
    """Mechmath chat (matches config.mechmath_chat_id)."""
    return make_chat(id=-1001091546301, title="MechMath", username="mechmath")


# =============================================================================
# Message Fixtures
# =============================================================================


def make_message(
    message_id: int = 1,
    chat: Chat | None = None,
    from_user: User | None = None,
    text: str | None = "Test message",
    date: int = 1704067200,
    reply_to_message: "Message | None" = None,
    sender_chat: Chat | None = None,
    **kwargs: Any,
) -> MagicMock:
    """
    Factory to create Message mock objects with sensible defaults.

    Uses MagicMock to allow flexible attribute assignment and method mocking.
    """
    if chat is None:
        chat = make_chat()
    if from_user is None:
        from_user = make_user()

    mock = MagicMock(spec=Message)
    mock.message_id = message_id
    mock.chat = chat
    mock.from_user = from_user
    mock.text = text
    mock.html_text = text
    mock.date = date
    mock.reply_to_message = reply_to_message
    mock.sender_chat = sender_chat
    mock.content_type = "text"
    mock.bot = None

    # Media attributes (default to None)
    mock.photo = None
    mock.audio = None
    mock.voice = None
    mock.sticker = None
    mock.video = None
    mock.video_note = None
    mock.animation = None
    mock.document = None

    # Topic/thread attributes
    mock.is_topic_message = False
    mock.message_thread_id = None

    # Reply methods as AsyncMocks
    mock.reply = AsyncMock(return_value=mock)
    mock.reply_photo = AsyncMock(return_value=mock)
    mock.reply_audio = AsyncMock(return_value=mock)
    mock.reply_voice = AsyncMock(return_value=mock)
    mock.reply_sticker = AsyncMock(return_value=mock)
    mock.reply_video = AsyncMock(return_value=mock)
    mock.reply_video_note = AsyncMock(return_value=mock)
    mock.reply_animation = AsyncMock(return_value=mock)
    mock.reply_document = AsyncMock(return_value=mock)
    mock.delete = AsyncMock()
    mock.edit_text = AsyncMock()
    mock.get_url = MagicMock(return_value="https://t.me/test/1")

    # Apply any additional kwargs
    for key, value in kwargs.items():
        setattr(mock, key, value)

    return mock


@pytest.fixture
def message(chat: Chat, user: User) -> MagicMock:
    """Default test message."""
    return make_message(chat=chat, from_user=user)


@pytest.fixture
def mechmath_message(mechmath_chat: Chat, user: User) -> MagicMock:
    """Message in mechmath chat."""
    return make_message(chat=mechmath_chat, from_user=user)


def make_message_with_photo(
    file_id: str = "photo_file_id_123",
    **kwargs: Any,
) -> MagicMock:
    """Factory for message with photo attachment."""
    msg = make_message(content_type="photo", **kwargs)
    photo = MagicMock(spec=PhotoSize)
    photo.file_id = file_id
    msg.photo = [photo]  # Photo is a list, last element is largest
    return msg


# =============================================================================
# Bot Fixtures
# =============================================================================


def make_bot(token: str = "42:ABC") -> MagicMock:
    """Factory to create Bot mock objects."""
    mock = MagicMock()
    mock.token = token
    mock.get_file = AsyncMock()
    mock.session = MagicMock()
    mock.session.api = MagicMock()
    mock.session.api.file_url = MagicMock(
        return_value="https://api.telegram.org/file/bot42:ABC/test.jpg"
    )
    return mock


@pytest.fixture
def bot() -> MagicMock:
    """Default test bot."""
    return make_bot()


# =============================================================================
# Update Fixtures
# =============================================================================


def make_update(
    update_id: int = 1,
    message: Message | MagicMock | None = None,
    edited_message: Message | MagicMock | None = None,
    callback_query: Any | None = None,
    inline_query: Any | None = None,
    **kwargs: Any,
) -> MagicMock:
    """Factory to create Update mock objects."""
    mock = MagicMock(spec=Update)
    mock.update_id = update_id
    mock.message = message
    mock.edited_message = edited_message
    mock.channel_post = None
    mock.edited_channel_post = None
    mock.inline_query = inline_query
    mock.chosen_inline_result = None
    mock.callback_query = callback_query
    mock.shipping_query = None
    mock.pre_checkout_query = None
    mock.poll = None
    mock.poll_answer = None
    mock.chat_member = None
    mock.my_chat_member = None
    mock.bot = None

    for key, value in kwargs.items():
        setattr(mock, key, value)

    return mock


@pytest.fixture
def update(message: MagicMock) -> MagicMock:
    """Default update with message."""
    return make_update(message=message)


# =============================================================================
# KekStorage Fixtures
# =============================================================================


@pytest.fixture
def mock_kek_storage():
    """Mock KekStorage with async methods."""
    storage = MagicMock()

    # Sample kek data
    sample_keks = [
        {
            "id": "rec123",
            "fields": {
                "Text": "Test kek 1",
                "AttachmentType": "text",
                "AttachmentFileID": None,
                "Attachment": None,
            },
        },
        {
            "id": "rec456",
            "fields": {
                "Text": "Test kek 2",
                "AttachmentType": "photo",
                "AttachmentFileID": "photo_123",
                "Attachment": [{"url": "https://example.com/photo.jpg"}],
            },
        },
    ]

    sample_users = [
        {
            "id": "user1",
            "fields": {
                "Name": "User One",
                "TelegramID": 123,
                "Author": ["rec123"],
                "Suggestor": [],
            },
        },
        {
            "id": "user2",
            "fields": {
                "Name": "User Two",
                "TelegramID": 456,
                "Author": ["rec456"],
                "Suggestor": ["rec123"],
            },
        },
    ]

    storage.async_all = AsyncMock(return_value=sample_keks)
    storage.async_all_users = AsyncMock(return_value=sample_users)
    storage.async_add = AsyncMock(return_value={"id": "new_rec", "fields": {}})
    storage.async_push = AsyncMock(return_value={"id": "pushed_rec", "fields": {}})
    storage.async_update_file_id = AsyncMock()

    return storage


# =============================================================================
# Handler Test Helpers
# =============================================================================


class HandlerTestContext:
    """Context manager for testing handlers with mocked dependencies."""

    def __init__(self):
        self.patches = []

    def patch_kek_storage(self, mock_storage):
        """Patch kek_storage in handlers."""
        p = patch("handlers.kek.kek.kek_storage", mock_storage)
        self.patches.append(p)
        p = patch("handlers.kek.kek_add.kek_storage", mock_storage)
        self.patches.append(p)
        p = patch("handlers.kek.kek_info.kek_storage", mock_storage)
        self.patches.append(p)
        return self

    def __enter__(self):
        for p in self.patches:
            p.start()
        return self

    def __exit__(self, *args):
        for p in self.patches:
            p.stop()


@pytest.fixture
def handler_context():
    """Fixture providing handler test context."""
    return HandlerTestContext()

