from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.utils.formatting import Bold, Code, Text, TextLink, as_line

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
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
async def help_(message: types.Message):
    return await message.reply(
        **Text(
            Bold("Список доступных команд"),
            ":",
            "\n\n",
            "• /kek — кек пек",
            "\n\n",
            "• /kek_add — отправляет цитируемое сообщение (reply) в предложку для новых кеков",
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
