from unittest.mock import AsyncMock, MagicMock

import pytest

from app import __main__ as app_main


@pytest.mark.parametrize(
    ("environment", "drop_pending_updates"),
    [("dev", True), ("test", True), ("prod", False)],
)
@pytest.mark.asyncio
async def test_polling_startup_removes_webhook(
    mocker, environment, drop_pending_updates
):
    bot = MagicMock()
    bot.delete_webhook = AsyncMock()
    dispatcher = MagicMock()
    dispatcher.start_polling = AsyncMock()
    mocker.patch.object(app_main, "Bot", return_value=bot)
    mocker.patch.object(app_main, "Dispatcher", return_value=dispatcher)
    mocker.patch.object(app_main.config, "environment", environment)

    await app_main.main()

    bot.delete_webhook.assert_awaited_once_with(
        drop_pending_updates=drop_pending_updates
    )
    dispatcher.start_polling.assert_awaited_once_with(bot)
