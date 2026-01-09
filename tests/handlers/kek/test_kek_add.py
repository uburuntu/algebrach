"""Tests for app/handlers/kek/kek_add.py"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.conftest import make_chat, make_message, make_user


class TestCmdKekAdd:
    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.async_add = AsyncMock(return_value={"id": "new_kek", "fields": {}})
        return storage

    @pytest.fixture
    def author(self):
        return make_user(id=111, first_name="Author")

    @pytest.fixture
    def suggestor(self):
        return make_user(id=222, first_name="Suggestor")

    @pytest.mark.asyncio
    async def test_adds_kek_to_storage(self, mock_storage, author, suggestor):
        reply_to = make_message(from_user=author, text="Quoted text")
        reply_to.html_text = "Quoted text"
        msg = make_message(from_user=suggestor, reply_to_message=reply_to)

        with patch("handlers.kek.kek_add.kek_storage", mock_storage):
            with patch(
                "handlers.kek.kek_add.extract_attachment_info_with_url",
                new=AsyncMock(return_value=(None, None, None, None)),
            ):
                from handlers.kek.kek_add import cmd_kek_add

                await cmd_kek_add(msg, reply_to)

        mock_storage.async_add.assert_awaited_once()
        call_kwargs = mock_storage.async_add.call_args.kwargs
        assert call_kwargs["author"] == author
        assert call_kwargs["suggestor"] == suggestor
        assert call_kwargs["text"] == "Quoted text"

    @pytest.mark.asyncio
    async def test_replies_with_confirmation(self, mock_storage, author, suggestor):
        reply_to = make_message(from_user=author, text="Kek text")
        reply_to.html_text = "Kek text"
        msg = make_message(from_user=suggestor, reply_to_message=reply_to)

        with patch("handlers.kek.kek_add.kek_storage", mock_storage):
            with patch(
                "handlers.kek.kek_add.extract_attachment_info_with_url",
                new=AsyncMock(return_value=(None, None, None, None)),
            ):
                from handlers.kek.kek_add import cmd_kek_add

                await cmd_kek_add(msg, reply_to)

        msg.reply.assert_awaited_once()
        reply_text = msg.reply.call_args.args[0]
        assert "✅" in reply_text
        assert "предложку" in reply_text


class TestCmdKekPush:
    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.async_push = AsyncMock(return_value={"id": "pushed", "fields": {}})
        return storage

    @pytest.mark.asyncio
    async def test_pushes_kek_to_list(self, mock_storage):
        author = make_user(id=123, first_name="Admin")
        reply_to = make_message(from_user=author, text="Push this")
        reply_to.html_text = "Push this"
        msg = make_message(from_user=author, reply_to_message=reply_to)

        with patch("handlers.kek.kek_add.kek_storage", mock_storage):
            with patch(
                "handlers.kek.kek_add.extract_attachment_info_with_url",
                new=AsyncMock(return_value=(None, None, None, None)),
            ):
                from handlers.kek.kek_add import cmd_kek_push

                await cmd_kek_push(msg, reply_to)

        mock_storage.async_push.assert_awaited_once()
        call_kwargs = mock_storage.async_push.call_args.kwargs
        assert call_kwargs["text"] == "Push this"


class TestCmdKekAddNoReply:
    @pytest.mark.asyncio
    async def test_tells_user_to_reply(self):
        msg = make_message()

        from handlers.kek.kek_add import cmd_kek_add_no_reply

        await cmd_kek_add_no_reply(msg)

        msg.reply.assert_awaited_once()
        reply_text = msg.reply.call_args.args[0]
        assert "реплаем" in reply_text


class TestCmdKekAddNonMechmath:
    @pytest.mark.asyncio
    async def test_tells_user_mechmath_only(self):
        other_chat = make_chat(id=-100999, title="Other Chat")
        msg = make_message(chat=other_chat)

        from handlers.kek.kek_add import cmd_kek_add_non_mechmath

        await cmd_kek_add_non_mechmath(msg)

        msg.reply.assert_awaited_once()
        reply_text = msg.reply.call_args.args[0]
        assert "@mechmath" in reply_text

