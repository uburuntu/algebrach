import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from handlers import basic, kek
from health import start_health_check_server
from middlewares.event_context import EventContextMiddleware
from middlewares.log_updates import LogUpdatesMiddleware
from settings import config

# Configure logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


async def main():
    """Initialize and start the Telegram bot."""
    logger.info(f"Starting {config.app_name} in {config.environment} environment")

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

    # Start health check server if enabled
    if config.enable_health_check:
        try:
            await start_health_check_server(port=config.health_check_port)
            logger.info(
                f"Health check endpoint available at http://0.0.0.0:{config.health_check_port}/health"
            )
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")

    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
