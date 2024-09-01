from aiogram.types import Message
from aiogram.utils.formatting import TextLink
from airtable.kek_storage import kek_storage
from common.tg import extract_attachment_info_with_url, reply_with_attachment


async def kek_add(message: Message, reply_to_message: Message):
    text = reply_to_message.html_text

    attachment_type, attachment_file_id, attachment_filename, attachment_url = (
        await extract_attachment_info_with_url(reply_to_message)
    )

    await kek_storage.async_add(
        author=reply_to_message.from_user,
        suggestor=message.from_user,
        text=text,
        attachment_type=attachment_type,
        attachment_file_id=attachment_file_id,
        attachment_filename=attachment_filename,
        attachment_url=attachment_url,
    )

    return await message.reply(
        f"✅ {TextLink('Кек', url=reply_to_message.get_url()).as_html()} отправлен в "
        "предложку"
    )


async def kek_push(message: Message, reply_to_message: Message):
    text = reply_to_message.html_text

    attachment_type, attachment_file_id, attachment_filename, attachment_url = (
        await extract_attachment_info_with_url(reply_to_message)
    )

    await kek_storage.async_push(
        author=reply_to_message.from_user,
        text=text,
        attachment_type=attachment_type,
        attachment_file_id=attachment_file_id,
        attachment_filename=attachment_filename,
        attachment_url=attachment_url,
    )

    return await reply_with_attachment(
        message, text, attachment_type, attachment_file_id
    )


async def kek_add_no_reply(message: Message):
    return await message.reply("↪️ Кеки нужно предлагать реплаем на сообщение")


async def kek_add_non_mechmath(message: Message):
    return await message.reply("➡️ Кеки можно предлагать только в @mechmath")
