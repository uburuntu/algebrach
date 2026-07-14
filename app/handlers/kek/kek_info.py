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
        kek["fields"].get("AttachmentType") or "text" for kek in keks
    )

    def format_user_list(field_name):
        ranked_users = sorted(
            (
                (
                    user["fields"].get("Name") or "Unknown",
                    user["fields"].get("TelegramID"),
                    len(user["fields"].get(field_name, [])),
                )
                for user in users
            ),
            key=lambda item: (-item[2], item[0].casefold()),
        )
        return [
            as_line(
                "• ",
                TextLink(name, url=f"tg://user?id={user_id}") if user_id else name,
                f": {count}",
            )
            for name, user_id, count in ranked_users
            if count > 0
        ][:5]

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
            *format_user_list("Author"),
            "\n",
            Bold("Топ 5 предложивших:"),
            "\n",
            *format_user_list("Suggestor"),
        ).as_kwargs(),
        disable_notification=True,
    )
