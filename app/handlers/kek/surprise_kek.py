import asyncio
import random

from datetime import timedelta

from aiogram.types import Chat, ChatPermissions, Message, User
from settings import config

from handlers.kek import cmd_kek


async def surprise_kek(message: Message, user: User, chat: Chat):
    surprise = await message.reply_animation(
        config.surprise_gif,
        caption="Предупреждал же, что кикну. Если не предупреждал, то",
    )

    if user.id in config.admin_ids or user.id in {
        m.user.id for m in await chat.get_administrators()
    }:
        result = await surprise.reply("... Ho против хозяев не восстану.")
        await asyncio.sleep(3)
        await surprise.delete()
        await result.delete()
        return await cmd_kek(message)

    readonly_minutes = random.randint(1, 60)
    await asyncio.sleep(1)

    result = await message.reply("/ROll")
    await asyncio.sleep(1)

    await result.edit_text(f"{readonly_minutes}")
    await asyncio.sleep(1)

    await result.edit_text(
        f"Эй, {user.mention_html(user.first_name)}. "
        f"Твой /kek обеспечил тебе {readonly_minutes} мин. ридонли. Поздравляю!"
    )
    await surprise.delete()
    return await message.chat.restrict(
        user.id,
        ChatPermissions(can_send_messages=False, can_send_other_messages=False),
        until_date=timedelta(minutes=readonly_minutes),
    )
