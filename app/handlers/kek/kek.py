import random

from aiogram.types import Message
from airtable.kek_storage import kek_storage
from common.tg import extract_attachment_file_id, reply_with_attachment
from settings import config


async def cmd_kek(message: Message):
    keks = await kek_storage.async_all()

    kek = random.choice(keks)
    kek_fields = kek["fields"]

    text = kek_fields.get("Text")
    attachment = kek_fields.get("Attachment")
    attachment_type = kek_fields.get("AttachmentType")
    attachment_file_id = kek_fields.get("AttachmentFileID")
    attachment_url_fallback = attachment and attachment[0]["url"]

    reply = await reply_with_attachment(
        message, text, attachment_type, attachment_file_id, attachment_url_fallback
    )

    if config.environment == "prod":
        if file_id := extract_attachment_file_id(reply):
            if file_id != attachment_file_id:
                await kek_storage.async_update_file_id(kek["id"], file_id)

    return reply
