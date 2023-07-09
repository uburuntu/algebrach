from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.utils.formatting import TextLink
from airtable.kek_storage import kek_storage
from settings import config


async def kek_add(message: Message, reply_to_message: Message):
    text = reply_to_message.html_text

    attachment_type = None
    attachment_url = None
    attachment_filename = None
    attachment_file_id = None

    if a := reply_to_message.photo:
        attachment_type = "photo"
        attachment_file_id = a[-1].file_id
    elif a := reply_to_message.audio:
        attachment_type = "audio"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name
    elif a := reply_to_message.voice:
        attachment_type = "voice"
        attachment_file_id = a.file_id
    elif a := reply_to_message.sticker:
        attachment_type = "sticker"
        attachment_file_id = a.file_id
    elif a := reply_to_message.video:
        attachment_type = "video"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name
    elif a := reply_to_message.video_note:
        attachment_type = "video_note"
        attachment_file_id = a.file_id
    elif a := reply_to_message.animation:
        attachment_type = "animation"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name
    elif a := reply_to_message.document:
        attachment_type = "document"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name

    if attachment_file_id:
        bot: Bot = Bot.get_current()
        file = await bot.get_file(attachment_file_id)
        attachment_url = bot.session.api.file_url(
            config.telegram_bot_token, file.file_path
        )

    await kek_storage.async_add(
        author=reply_to_message.from_user,
        suggestor=message.from_user,
        text=text,
        attachment_type=attachment_type,
        attachment_url=attachment_url,
        attachment_filename=attachment_filename,
        attachment_file_id=attachment_file_id,
    )

    return await message.reply(
        f"✅ {TextLink('Кек', url=reply_to_message.get_url()).as_html()} отправлен в "
        "предложку"
    )


async def kek_push(message: Message, reply_to_message: Message):
    text = reply_to_message.html_text

    attachment_type = None
    attachment_url = None
    attachment_filename = None
    attachment_file_id = None

    if a := reply_to_message.photo:
        attachment_type = "photo"
        attachment_file_id = a[-1].file_id
    elif a := reply_to_message.audio:
        attachment_type = "audio"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name
    elif a := reply_to_message.voice:
        attachment_type = "voice"
        attachment_file_id = a.file_id
    elif a := reply_to_message.sticker:
        attachment_type = "sticker"
        attachment_file_id = a.file_id
    elif a := reply_to_message.video:
        attachment_type = "video"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name
    elif a := reply_to_message.video_note:
        attachment_type = "video_note"
        attachment_file_id = a.file_id
    elif a := reply_to_message.animation:
        attachment_type = "animation"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name
    elif a := reply_to_message.document:
        attachment_type = "document"
        attachment_file_id = a.file_id
        attachment_filename = a.file_name

    if attachment_file_id:
        bot: Bot = Bot.get_current()
        file = await bot.get_file(attachment_file_id)
        attachment_url = bot.session.api.file_url(
            config.telegram_bot_token, file.file_path
        )

    kek = await kek_storage.async_push(
        author=reply_to_message.from_user,
        text=text,
        attachment_type=attachment_type,
        attachment_url=attachment_url,
        attachment_filename=attachment_filename,
        attachment_file_id=attachment_file_id,
    )

    kek_fields = kek["fields"]

    text = kek_fields.get("Text")
    attachment_type = kek_fields.get("AttachmentType")
    attachment = kek_fields.get("Attachment", [None])[0]
    attachment_file_id = kek_fields.get("AttachmentFileID")

    async def send(method):
        try:
            return await method(attachment_file_id, caption=text)
        except TelegramBadRequest:
            reply = await method(attachment["url"], caption=text)
            if config.environment == "prod":
                # todo: fix file_id in base in case of exceptions
                _kek_id = kek["id"]
            return reply

    match attachment_type:
        case "photo":
            return await send(message.reply_photo)
        case "audio":
            return await send(message.reply_audio)
        case "voice":
            return await send(message.reply_voice)
        case "sticker":
            return await send(message.reply_sticker)
        case "video":
            return await send(message.reply_video)
        case "video_note":
            return await send(message.reply_video_note)
        case "animation":
            return await send(message.reply_animation)
        case "document":
            return await send(message.reply_document)
        case None:
            return await message.reply(text, disable_web_page_preview=False)

    return await message.reply(
        f"✅ {TextLink('Кек', url=reply_to_message.get_url()).as_html()} принят!"
    )


async def kek_add_no_reply(message: Message):
    return await message.reply("↪️ Кеки нужно предлагать реплаем на сообщение")


async def kek_add_non_mechmath(message: Message):
    return await message.reply("➡️ Кеки можно предлагать только в @mechmath")
