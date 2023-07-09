from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.middlewares.user_context import UserContextMiddleware
from aiogram.types import TelegramObject, Update


class EventContextMiddleware(UserContextMiddleware):
    """
    Extracts event's actor, chat and thread_id to the handler's parameters
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Update):
            raise RuntimeError("Got an unexpected event type")

        chat, user, thread_id = self.resolve_event_context(event=event)

        if user is not None:
            data["user"] = user

        if chat is not None:
            data["chat"] = chat

        if thread_id is not None:
            data["thread_id"] = thread_id

        return await handler(event, data)
