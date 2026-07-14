from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.utils.formatting import Bold, Code, Text, TextLink, as_line

if TYPE_CHECKING:
    from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    return await message.reply(
        **Text(
            Bold("Приветствую!"),
            "\n\n",
            "Я бот чата мехмата МГУ (@mechmath) и имею кучу полезных функций. ",
            "Узнать полный список доступных команд можно в /help.",
            "\n\n",
            as_line("Обратная связь: ", Code("@rm_bk"), " 👋🏻"),
        ).as_kwargs()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    return await message.reply(
        **Text(
            Bold("Список доступных команд"),
            ":",
            "\n\n",
            "• /kek — кек пек",
            "\n\n",
            "• /kek_add — отправляет цитируемое сообщение (reply) в предложку кеков",
            "\n\n",
            "• /kek_info — показывает статистику кеков",
            "\n\n",
            as_line("Обратная связь: ", Code("@rm_bk")),
            as_line(
                "Код бота: ",
                TextLink(
                    "uburuntu/algebrach", url="https://github.com/uburuntu/algebrach"
                ),
            ),
        ).as_kwargs()
    )
