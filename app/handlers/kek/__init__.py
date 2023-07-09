from aiogram import F, Router
from aiogram.filters import Command
from common.utils import percent_chance
from middlewares.skip_anonymous import SkipAnonymousMessagesMiddleware
from middlewares.throttle_users import ThrottleUsersMiddleware
from settings import config

from handlers.kek.kek import cmd_kek
from handlers.kek.kek_add import (
    kek_add,
    kek_add_no_reply,
    kek_add_non_mechmath,
    kek_push,
)
from handlers.kek.surprise_kek import surprise_kek

# Respectfully migrated from: https://github.com/arvego/mm-randbot/blob/master/commands/kek.py

router = Router()

router.message.middleware(SkipAnonymousMessagesMiddleware())
router.message.middleware(ThrottleUsersMiddleware())

router.message.register(
    surprise_kek,
    Command("kek"),
    F.chat.id == config.mechmath_chat_id,
    lambda _: percent_chance(33),
)

router.message.register(cmd_kek, Command("kek"))

router.message.register(
    kek_add_non_mechmath, Command("kek_add"), F.chat.id != config.mechmath_chat_id
)

router.message.register(
    kek_add,
    Command("kek_add"),
    F.chat.id == config.mechmath_chat_id,
    F.reply_to_message.as_("reply_to_message"),
)

router.message.register(
    kek_push,
    Command("kek_push"),
    F.from_user.id == config.rmbk_id,
    F.reply_to_message.as_("reply_to_message"),
)


router.message.register(
    kek_add_no_reply,
    Command("kek_add"),
    F.chat.id == config.mechmath_chat_id,
)
