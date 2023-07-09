import asyncio

from aiogram import Bot, Dispatcher
from handlers import basic, kek
from middlewares.event_context import EventContextMiddleware
from middlewares.log_updates import LogUpdatesMiddleware
from settings import config


async def main():
    bot = Bot(
        token=config.telegram_bot_token,
        parse_mode="HTML",
        disable_web_page_preview=True,
        protect_content=False,
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
