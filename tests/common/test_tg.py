"""Tests for app/common/tg.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from aiogram.types import (
    Animation,
    Audio,
    CallbackQuery,
    Document,
    InlineQuery,
    PhotoSize,
    Sticker,
    Video,
    VideoNote,
    Voice,
)

from app.common.tg import (
    chat_info,
    create_sensitive_url_from_file_id,
    decompose_update,
    extract_attachment_file_id,
    extract_attachment_info,
    message_info,
    reply_with_attachment,
    user_info,
)
from tests.conftest import (
    make_bot,
    make_chat,
    make_message,
    make_update,
    make_user,
)

# =============================================================================
# user_info tests
# =============================================================================


class TestUserInfo:
    def test_basic_user(self):
        user = make_user(id=123, first_name="John")
        result = user_info(user)
        assert result == "John (123, en)"

    def test_user_with_last_name(self):
        user = make_user(id=123, first_name="John", last_name="Doe")
        result = user_info(user)
        assert result == "John Doe (123, en)"

    def test_user_with_username(self):
        user = make_user(id=123, first_name="John", username="johndoe")
        result = user_info(user)
        assert result == "John (123, @johndoe, en)"

    def test_user_full_info(self):
        user = make_user(
            id=123,
            first_name="John",
            last_name="Doe",
            username="johndoe",
            language_code="ru",
        )
        result = user_info(user)
        assert result == "John Doe (123, @johndoe, ru)"

    def test_user_no_language_code(self):
        user = make_user(id=123, first_name="John", language_code=None)
        result = user_info(user)
        assert result == "John (123)"

    def test_user_with_sender_chat_returns_chat_info(self):
        user = make_user(id=123, first_name="John")
        sender_chat = make_chat(id=-100123, type="channel", title="My Channel")
        result = user_info(user, sender_chat)
        assert "channel" in result
        assert "My Channel" in result


# =============================================================================
# chat_info tests
# =============================================================================


class TestChatInfo:
    def test_private_chat(self):
        chat = make_chat(id=123, type="private", title=None)
        result = chat_info(chat)
        assert result == "private"

    def test_supergroup_chat(self):
        chat = make_chat(id=-1001234, type="supergroup", title="Test Group")
        result = chat_info(chat)
        assert result == "supergroup | Test Group (-1001234)"

    def test_group_chat_with_username(self):
        chat = make_chat(
            id=-1001234, type="supergroup", title="Public Group", username="pubgroup"
        )
        result = chat_info(chat)
        assert result == "supergroup | Public Group (-1001234, @pubgroup)"

    def test_channel(self):
        chat = make_chat(id=-1001234, type="channel", title="My Channel")
        result = chat_info(chat)
        assert result == "channel | My Channel (-1001234)"


# =============================================================================
# message_info tests
# =============================================================================


class TestMessageInfo:
    def test_text_message(self):
        msg = make_message(message_id=42, text="Hello world")
        result = message_info(msg)
        assert result == "42 | Hello world"

    def test_text_message_truncated(self):
        long_text = "A" * 100
        msg = make_message(message_id=1, text=long_text)
        result = message_info(msg)
        assert result == f"1 | {'A' * 50}"
        assert len(result.split(" | ")[1]) == 50

    def test_multiline_text_becomes_single_line(self):
        msg = make_message(message_id=1, text="Hello\nWorld\nTest")
        result = message_info(msg)
        assert result == "1 | Hello World Test"

    def test_non_text_message(self):
        msg = make_message(message_id=5, text=None, content_type="photo")
        result = message_info(msg)
        assert result == "5 | type: photo"


# =============================================================================
# decompose_update tests
# =============================================================================


class TestDecomposeUpdate:
    def test_message_update(self):
        msg = make_message(message_id=1, text="Hello")
        update = make_update(message=msg)

        f, user, _sender_chat, chat, info = decompose_update(update)

        assert f == msg
        assert user == msg.from_user
        assert chat == msg.chat
        assert "Hello" in info

    def test_edited_message_update(self):
        msg = make_message(message_id=1, text="Edited text")
        update = make_update(edited_message=msg)

        f, _user, _sender_chat, _chat, info = decompose_update(update)

        assert f == msg
        assert "[edited]" in info

    def test_inline_query_update(self):
        user = make_user()
        inline_query = MagicMock(spec=InlineQuery)
        inline_query.from_user = user
        inline_query.query = "search term"
        update = make_update(inline_query=inline_query)

        f, user_result, _sender_chat, _chat, info = decompose_update(update)

        assert f == inline_query
        assert user_result == user
        assert "search term" in info

    def test_callback_query_update(self):
        user = make_user()
        msg = make_message()
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.from_user = user
        callback_query.message = msg
        callback_query.data = "button_clicked"
        update = make_update(callback_query=callback_query)

        f, user_result, _sender_chat, chat, info = decompose_update(update)

        assert f == callback_query
        assert user_result == user
        assert chat == msg.chat
        assert info == "button_clicked"


# =============================================================================
# extract_attachment_info tests
# =============================================================================


class TestExtractAttachmentInfo:
    def test_no_attachment(self):
        msg = make_message()
        att_type, file_id, filename = extract_attachment_info(msg)

        assert att_type is None
        assert file_id is None
        assert filename is None

    def test_photo_attachment(self):
        msg = make_message()
        photo = MagicMock(spec=PhotoSize)
        photo.file_id = "photo_abc123"
        msg.photo = [photo]  # List of sizes, last is largest

        att_type, file_id, filename = extract_attachment_info(msg)

        assert att_type == "photo"
        assert file_id == "photo_abc123"
        assert filename is None

    def test_audio_attachment(self):
        msg = make_message()
        audio = MagicMock(spec=Audio)
        audio.file_id = "audio_abc123"
        audio.file_name = "song.mp3"
        msg.audio = audio

        att_type, file_id, filename = extract_attachment_info(msg)

        assert att_type == "audio"
        assert file_id == "audio_abc123"
        assert filename == "song.mp3"

    def test_voice_attachment(self):
        msg = make_message()
        voice = MagicMock(spec=Voice)
        voice.file_id = "voice_abc123"
        msg.voice = voice

        att_type, file_id, _filename = extract_attachment_info(msg)

        assert att_type == "voice"
        assert file_id == "voice_abc123"

    def test_sticker_attachment(self):
        msg = make_message()
        sticker = MagicMock(spec=Sticker)
        sticker.file_id = "sticker_abc123"
        msg.sticker = sticker

        att_type, file_id, _filename = extract_attachment_info(msg)

        assert att_type == "sticker"
        assert file_id == "sticker_abc123"

    def test_video_attachment(self):
        msg = make_message()
        video = MagicMock(spec=Video)
        video.file_id = "video_abc123"
        video.file_name = "clip.mp4"
        msg.video = video

        att_type, file_id, filename = extract_attachment_info(msg)

        assert att_type == "video"
        assert file_id == "video_abc123"
        assert filename == "clip.mp4"

    def test_video_note_attachment(self):
        msg = make_message()
        video_note = MagicMock(spec=VideoNote)
        video_note.file_id = "videonote_abc123"
        msg.video_note = video_note

        att_type, file_id, _filename = extract_attachment_info(msg)

        assert att_type == "video_note"
        assert file_id == "videonote_abc123"

    def test_animation_attachment(self):
        msg = make_message()
        animation = MagicMock(spec=Animation)
        animation.file_id = "animation_abc123"
        animation.file_name = "funny.gif"
        msg.animation = animation

        att_type, file_id, filename = extract_attachment_info(msg)

        assert att_type == "animation"
        assert file_id == "animation_abc123"
        assert filename == "funny.gif"

    def test_document_attachment(self):
        msg = make_message()
        document = MagicMock(spec=Document)
        document.file_id = "doc_abc123"
        document.file_name = "report.pdf"
        msg.document = document

        att_type, file_id, filename = extract_attachment_info(msg)

        assert att_type == "document"
        assert file_id == "doc_abc123"
        assert filename == "report.pdf"


class TestExtractAttachmentFileId:
    def test_returns_file_id(self):
        msg = make_message()
        photo = MagicMock(spec=PhotoSize)
        photo.file_id = "photo_xyz"
        msg.photo = [photo]

        file_id = extract_attachment_file_id(msg)

        assert file_id == "photo_xyz"

    def test_returns_none_when_no_attachment(self):
        msg = make_message()
        file_id = extract_attachment_file_id(msg)
        assert file_id is None


# =============================================================================
# create_sensitive_url_from_file_id tests
# =============================================================================


class TestCreateSensitiveUrlFromFileId:
    @pytest.mark.asyncio
    async def test_creates_url(self):
        bot = make_bot(token="123:TOKEN")
        file_mock = MagicMock()
        file_mock.file_path = "photos/file_1.jpg"
        bot.get_file = AsyncMock(return_value=file_mock)
        bot.session.api.file_url = MagicMock(
            return_value="https://api.telegram.org/file/bot123:TOKEN/photos/file_1.jpg"
        )

        result = await create_sensitive_url_from_file_id(bot, "file_id_123")

        bot.get_file.assert_awaited_once_with("file_id_123")
        assert "api.telegram.org" in result
        assert "file_1.jpg" in result


# =============================================================================
# reply_with_attachment tests
# =============================================================================


class TestReplyWithAttachment:
    @pytest.mark.asyncio
    async def test_reply_text_only(self):
        msg = make_message()

        await reply_with_attachment(msg, "Hello!", None, None)

        msg.reply.assert_awaited_once_with("Hello!", disable_web_page_preview=False)

    @pytest.mark.asyncio
    async def test_reply_photo(self):
        msg = make_message()

        await reply_with_attachment(msg, "Caption", "photo", "photo_id_123")

        msg.reply_photo.assert_awaited_once_with("photo_id_123", caption="Caption")

    @pytest.mark.asyncio
    async def test_reply_audio(self):
        msg = make_message()

        await reply_with_attachment(msg, "Listen", "audio", "audio_id")

        msg.reply_audio.assert_awaited_once_with("audio_id", caption="Listen")

    @pytest.mark.asyncio
    async def test_reply_voice(self):
        msg = make_message()

        await reply_with_attachment(msg, "Voice", "voice", "voice_id")

        msg.reply_voice.assert_awaited_once_with("voice_id", caption="Voice")

    @pytest.mark.asyncio
    async def test_reply_sticker(self):
        msg = make_message()

        await reply_with_attachment(msg, "", "sticker", "sticker_id")

        msg.reply_sticker.assert_awaited_once_with("sticker_id", caption="")

    @pytest.mark.asyncio
    async def test_reply_video(self):
        msg = make_message()

        await reply_with_attachment(msg, "Video", "video", "video_id")

        msg.reply_video.assert_awaited_once_with("video_id", caption="Video")

    @pytest.mark.asyncio
    async def test_reply_video_note(self):
        msg = make_message()

        await reply_with_attachment(msg, "", "video_note", "videonote_id")

        msg.reply_video_note.assert_awaited_once_with("videonote_id", caption="")

    @pytest.mark.asyncio
    async def test_reply_animation(self):
        msg = make_message()

        await reply_with_attachment(msg, "GIF", "animation", "anim_id")

        msg.reply_animation.assert_awaited_once_with("anim_id", caption="GIF")

    @pytest.mark.asyncio
    async def test_reply_document(self):
        msg = make_message()

        await reply_with_attachment(msg, "Doc", "document", "doc_id")

        msg.reply_document.assert_awaited_once_with("doc_id", caption="Doc")

    @pytest.mark.asyncio
    async def test_fallback_url_on_telegram_bad_request(self):
        from aiogram.exceptions import TelegramBadRequest

        msg = make_message()
        msg.reply_photo = AsyncMock(
            side_effect=[
                TelegramBadRequest(method="sendPhoto", message="file not found"),
                MagicMock(),  # Second call succeeds
            ]
        )

        await reply_with_attachment(
            msg, "Caption", "photo", "bad_id", "https://fallback.url/photo.jpg"
        )

        assert msg.reply_photo.await_count == 2
        msg.reply_photo.assert_awaited_with(
            "https://fallback.url/photo.jpg", caption="Caption"
        )
