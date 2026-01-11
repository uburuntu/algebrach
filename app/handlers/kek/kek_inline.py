"""Inline query handler for keks.

Allows users to search and send keks from any chat by typing @algebrach_bot.
"""

import random
import uuid

from typing import TYPE_CHECKING

from aiogram import Bot, F, Router, html
from aiogram.types import (
    ChosenInlineResult,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from airtable.kek_storage import kek_storage
from common.utils import one_liner

if TYPE_CHECKING:
    from typing import Any

router = Router(name="kek_inline")

CACHE_TIME = 5 * 60


def get_text_keks(keks: list[dict]) -> list[dict]:
    """Filter to text-only keks (no attachments)."""
    return [
        k
        for k in keks
        if k["fields"].get("Text") and not k["fields"].get("AttachmentType")
    ]


def search_keks(keks: list[dict], query: str, limit: int = 10) -> list[dict]:
    """Case-insensitive substring search with early exit on limit."""
    query_lower = query.lower()
    results = []
    for k in keks:
        if query_lower in k["fields"]["Text"].lower():
            results.append(k)
            if len(results) >= limit:
                break
    return results


def kek_to_result(kek: dict) -> InlineQueryResultArticle:
    """Convert kek record to InlineQueryResultArticle."""
    text = kek["fields"]["Text"]
    preview = one_liner(text, cut_len=100)

    return InlineQueryResultArticle(
        id=kek["id"],
        title=preview[:50] or "Кек",
        description=preview[50:100] if len(preview) > 50 else None,
        input_message_content=InputTextMessageContent(
            message_text=html.quote(text),
        ),
    )


# Keyboard required to receive inline_message_id in ChosenInlineResult
PLACEHOLDER_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="⏳", callback_data="noop")]]
)


@router.inline_query(F.query == "")
async def inline_kek_random(query: InlineQuery) -> Any:
    """Show option to send a random kek."""
    result = InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="🎲 Случайный кек",
        description="Отправить случайный кек из базы",
        input_message_content=InputTextMessageContent(
            message_text="🎲 Выбираю кек...",
        ),
        reply_markup=PLACEHOLDER_KEYBOARD,
    )
    await query.answer([result], cache_time=CACHE_TIME, is_personal=False)


@router.inline_query(F.query != "")
async def inline_kek_search(query: InlineQuery) -> Any:
    """Search keks by text and return matching results."""
    keks = await kek_storage.async_all()
    text_keks = get_text_keks(keks)
    matches = search_keks(text_keks, query.query, limit=10)

    if not matches:
        result = InlineQueryResultArticle(
            id="not_found",
            title="😢 Кеков не найдено",
            description=f"По запросу «{query.query[:30]}»",
            input_message_content=InputTextMessageContent(
                message_text=f"🔍 Кеков по запросу «{html.quote(query.query)}» не найдено",
            ),
        )
        await query.answer([result], cache_time=CACHE_TIME, is_personal=False)
        return

    results = [kek_to_result(k) for k in matches]
    await query.answer(results, cache_time=CACHE_TIME, is_personal=False)


@router.chosen_inline_result()
async def chosen_random_kek(chosen: ChosenInlineResult, bot: Bot) -> None:
    """Edit placeholder message with actual random kek."""
    if not chosen.inline_message_id:
        return

    keks = await kek_storage.async_all()
    text_keks = get_text_keks(keks)

    if not text_keks:
        await bot.edit_message_text(
            inline_message_id=chosen.inline_message_id,
            text="😢 Кеков пока нет",
        )
        return

    kek = random.choice(text_keks)
    await bot.edit_message_text(
        inline_message_id=chosen.inline_message_id,
        text=html.quote(kek["fields"]["Text"]),
        reply_markup=None,
    )
