from collections import Counter

from aiogram.types import Message
from aiogram.utils.formatting import Bold, Text, as_line
from airtable.kek_storage import kek_storage


async def cmd_kek_info(message: Message):
    keks = await kek_storage.async_all()
    total_keks = len(keks)

    attachment_types = Counter(
        kek["fields"].get("AttachmentType", "text") for kek in keks
    )

    return await message.reply(
        **Text(
            Bold("Всего кеков в базе:"),
            f" {total_keks}",
            "\n\n",
            Bold("По типу:"),
            "\n",
            *[
                as_line("• ", att_type, f": {count}")
                for att_type, count in attachment_types.most_common()
            ],
        ).as_kwargs()
    )
