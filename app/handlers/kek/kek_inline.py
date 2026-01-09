"""Inline query handler for keks.

Allows users to search and send keks from any chat by typing @algebrach_bot.
"""

import random
import uuid

from typing import TYPE_CHECKING

from aiogram import Bot, F, Router
from aiogram.types import (
    ChosenInlineResult,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from airtable.kek_storage import kek_storage
from common.utils import one_liner

if TYPE_CHECKING:
    from typing import Any

router = Router(name="kek_inline")

CACHE_TIME = 5 * 60  # 5 minutes, shared across users


def get_text_keks(keks: list[dict]) -> list[dict]:
    """Filter to text-only keks (no attachments)."""
    return [
        k
        for k in keks
        if k["fields"].get("Text") and not k["fields"].get("AttachmentType")
    ]


def search_keks(keks: list[dict], query: str) -> list[dict]:
    """Simple case-insensitive substring search."""
    query_lower = query.lower()
    return [k for k in keks if query_lower in k["fields"]["Text"].lower()]


def kek_to_result(kek: dict) -> InlineQueryResultArticle:
    """Convert kek to inline result with placeholder message."""
    text = kek["fields"]["Text"]
    kek_id = kek["id"]
    preview = one_liner(text, cut_len=100)

    return InlineQueryResultArticle(
        id=kek_id,  # Use kek ID to retrieve it later
        title=preview[:50] or "Кек",
        description=preview[50:100] if len(preview) > 50 else None,
        input_message_content=InputTextMessageContent(
            message_text="🎲 Выбираю кек...",
        ),
    )


@router.inline_query(F.query == "")
async def inline_kek_random(query: InlineQuery) -> Any:
    """Empty query - offer to send random kek."""
    result = InlineQueryResultArticle(
        id=str(uuid.uuid4()),
        title="🎲 Случайный кек",
        description="Отправить случайный кек из базы",
        input_message_content=InputTextMessageContent(
            message_text="🎲 Выбираю кек...",
        ),
    )
    await query.answer([result], cache_time=CACHE_TIME, is_personal=False)


@router.inline_query(F.query != "")
async def inline_kek_search(query: InlineQuery) -> Any:
    """Non-empty query - search keks by text."""
    keks = await kek_storage.async_all()
    text_keks = get_text_keks(keks)
    matches = search_keks(text_keks, query.query)[:10]

    if not matches:
        result = InlineQueryResultArticle(
            id="not_found",
            title="😢 Кеков не найдено",
            description=f"По запросу «{query.query[:30]}»",
            input_message_content=InputTextMessageContent(
                message_text=f"🔍 Кеков по запросу «{query.query}» не найдено",
            ),
        )
        await query.answer([result], cache_time=CACHE_TIME, is_personal=False)
        return

    results = [kek_to_result(k) for k in matches]
    await query.answer(results, cache_time=CACHE_TIME, is_personal=False)


@router.chosen_inline_result()
async def chosen_kek_result(chosen: ChosenInlineResult, bot: Bot) -> None:
    """Replace placeholder with actual kek text."""
    if not chosen.inline_message_id:
        return

    keks = await kek_storage.async_all()
    text_keks = get_text_keks(keks)

    # If ID matches a kek, use that; otherwise pick random
    kek = next((k for k in text_keks if k["id"] == chosen.result_id), None)
    if not kek:
        kek = random.choice(text_keks) if text_keks else None

    if not kek:
        await bot.edit_message_text(
            inline_message_id=chosen.inline_message_id,
            text="😢 Кеков пока нет",
        )
        return

    await bot.edit_message_text(
        inline_message_id=chosen.inline_message_id,
        text=kek["fields"]["Text"],
    )
