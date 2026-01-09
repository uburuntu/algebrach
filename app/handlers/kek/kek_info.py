from collections import Counter
from typing import TYPE_CHECKING

from aiogram.utils.formatting import Bold, Text, TextLink, as_line
from airtable.kek_storage import kek_storage

if TYPE_CHECKING:
    from aiogram.types import Message


async def cmd_kek_info(message: Message):
    keks = await kek_storage.async_all()
    users = await kek_storage.async_all_users()

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
                "• ", TextLink(name, url=f"tg://user?id={user_ids[name]}"), f": {count}"
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
