import logging

from collections import Counter

from aiogram.types import Message
from aiogram.utils.formatting import Bold, Text, TextLink, as_line
from airtable.kek_storage import kek_storage

logger = logging.getLogger(__name__)


async def cmd_kek_info(message: Message):
    """
    Handle /kek_info command - display statistics about keks.

    Shows:
    - Total number of keks
    - Breakdown by attachment type
    - Top 5 authors
    - Top 5 suggestors

    Args:
        message: Incoming Telegram message

    Returns:
        Statistics message or error message
    """
    try:
        keks = await kek_storage.async_all()
        users = await kek_storage.async_all_users()

        if not keks:
            await message.reply("😔 No keks in the database yet!")
            return None

        attachment_types = Counter(
            kek["fields"].get("AttachmentType", "text") for kek in keks
        )
        authors = Counter()
        suggestors = Counter()
        user_ids = {}

        for user in users:
            name = user["fields"].get("Name", "Unknown")
            user_ids[name] = user["fields"].get("TelegramID", "")
            authors[name] = len(user["fields"].get("Author", []))
            suggestors[name] = len(user["fields"].get("Suggestor", []))

        def format_user_list(user_counter):
            return [
                as_line(
                    "• ",
                    TextLink(name, url=f"tg://user?id={user_ids[name]}"),
                    f": {count}",
                )
                for name, count in user_counter.most_common(6)
            ]

        return await message.reply(
            **Text(
                Bold("Всего кеков в базе:"),
                f" {len(keks)}",
                "\n\n",
                Bold("По типу:"),
                "\n",
                *[
                    as_line("• ", att_type, f": {count}")
                    for att_type, count in attachment_types.most_common()
                ],
                "\n",
                Bold("Топ 5 авторов:"),
                "\n",
                *format_user_list(authors),
                "\n",
                Bold("Топ 5 предложивших:"),
                "\n",
                *format_user_list(suggestors),
            ).as_kwargs(),
            disable_notification=True,
        )

    except TimeoutError:
        logger.error("Airtable query timed out in cmd_kek_info")
        await message.reply(
            "⏱ Service is temporarily slow. Please try again in a moment."
        )
        return None
    except Exception as e:
        logger.exception("Unexpected error in cmd_kek_info")
        await message.reply("❌ An unexpected error occurred. Please try again later.")
        return None
