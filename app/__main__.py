import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from handlers import basic, kek
from middlewares.event_context import EventContextMiddleware
from middlewares.log_updates import LogUpdatesMiddleware
from settings import config


async def main():
    default = DefaultBotProperties(
        parse_mode="HTML",
        disable_notification=True,
        protect_content=False,
        allow_sending_without_reply=True,
        link_preview_is_disabled=True,
    )

    bot = Bot(
        token=config.telegram_bot_token,
        default=default,
    )

    dp = Dispatcher()

    dp.update.outer_middleware(LogUpdatesMiddleware())
    dp.update.middleware(EventContextMiddleware())

    dp.include_routers(basic.router, kek.router)

    if config.environment != "prod":
        await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
