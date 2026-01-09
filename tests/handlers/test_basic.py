"""Tests for app/handlers/basic.py"""

import pytest

from app.handlers.basic import cmd_help, cmd_start

from tests.conftest import make_message


class TestCmdStart:
    @pytest.mark.asyncio
    async def test_replies_with_greeting(self):
        msg = make_message()

        await cmd_start(msg)

        msg.reply.assert_awaited_once()
        call_kwargs = msg.reply.call_args.kwargs
        assert "text" in call_kwargs
        assert "Приветствую" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_mentions_help_command(self):
        msg = make_message()

        await cmd_start(msg)

        call_kwargs = msg.reply.call_args.kwargs
        assert "/help" in call_kwargs["text"]


class TestCmdHelp:
    @pytest.mark.asyncio
    async def test_replies_with_commands_list(self):
        msg = make_message()

        await cmd_help(msg)

        msg.reply.assert_awaited_once()
        call_kwargs = msg.reply.call_args.kwargs
        assert "text" in call_kwargs

    @pytest.mark.asyncio
    async def test_includes_kek_command(self):
        msg = make_message()

        await cmd_help(msg)

        call_kwargs = msg.reply.call_args.kwargs
        assert "/kek" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_includes_kek_add_command(self):
        msg = make_message()

        await cmd_help(msg)

        call_kwargs = msg.reply.call_args.kwargs
        assert "/kek_add" in call_kwargs["text"]

    @pytest.mark.asyncio
    async def test_includes_github_link(self):
        msg = make_message()

        await cmd_help(msg)

        call_kwargs = msg.reply.call_args.kwargs
        assert "uburuntu/algebrach" in call_kwargs["text"]

