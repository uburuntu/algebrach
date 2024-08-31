import random

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from airtable.kek_storage import kek_storage
from settings import config


async def cmd_kek(message: Message):
    keks = await kek_storage.async_all()

    kek = random.choice(keks)
    kek_fields = kek["fields"]

    text = kek_fields.get("Text")
    attachment_type = kek_fields.get("AttachmentType")
    attachment = kek_fields.get("Attachment", [None])[0]
    attachment_file_id = kek_fields.get("AttachmentFileID")

    async def send(method):
        """Try to send a message by `file_id` or by value
        in case of broken `file_id`"""
        try:
            return await method(attachment_file_id, caption=text)
        except TelegramBadRequest:
            reply = await method(attachment["url"], caption=text)
            if config.environment == "prod":
                # todo: fix `file_id` in base in case of exceptions
                _kek_id = kek["id"]
            return reply

    match attachment_type:
        case "animation":
            return await send(message.reply_animation)
        case "audio":
            return await send(message.reply_audio)
        case "document":
            return await send(message.reply_document)
        case "photo":
            return await send(message.reply_photo)
        case "sticker":
            return await send(message.reply_sticker)
        case "video":
            return await send(message.reply_video)
        case "video_note":
            return await send(message.reply_video_note)
        case "voice":
            return await send(message.reply_voice)
        case None:
            return await message.reply(text, disable_web_page_preview=False)
