import logging

from aiogram.types import Message
from aiogram.utils.formatting import TextLink
from airtable.kek_storage import kek_storage
from common.tg import extract_attachment_info_with_url, reply_with_attachment, user_info

logger = logging.getLogger(__name__)


async def cmd_kek_add(message: Message, reply_to_message: Message):
    """
    Handle /kek_add command - submit a kek suggestion for moderation.

    Args:
        message: Command message from suggestor
        reply_to_message: The message being suggested as a kek

    Returns:
        Confirmation message or error message
    """
    try:
        text = reply_to_message.html_text

        # Validate text length (Telegram message limit)
        if text and len(text) > 4096:
            await message.reply("❌ Text too long (max 4096 characters)")
            return None

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

        logger.info(
            f"Kek suggestion added by {user_info(message.from_user)} "
            f"for message by {user_info(reply_to_message.from_user)}"
        )

        return await message.reply(
            f"✅ {TextLink('Кек', url=reply_to_message.get_url()).as_html()} отправлен в "
            "предложку"
        )

    except TimeoutError:
        logger.error("Airtable query timed out in cmd_kek_add")
        await message.reply(
            "⏱ Service is temporarily slow. Please try again in a moment."
        )
        return None
    except Exception as e:
        logger.exception("Unexpected error in cmd_kek_add")
        await message.reply("❌ An unexpected error occurred. Please try again later.")
        return None


async def cmd_kek_push(message: Message, reply_to_message: Message):
    """
    Handle /kek_push command (admin only) - directly add a kek to the list.

    Args:
        message: Command message from admin
        reply_to_message: The message being pushed as a kek

    Returns:
        The pushed kek message or error message
    """
    try:
        text = reply_to_message.html_text

        # Validate text length
        if text and len(text) > 4096:
            await message.reply("❌ Text too long (max 4096 characters)")
            return None

        attachment_type, attachment_file_id, attachment_filename, attachment_url = (
            await extract_attachment_info_with_url(reply_to_message)
        )

        # Audit log for admin action
        logger.warning(
            f"AUDIT: Admin action - kek_push by {user_info(message.from_user)} "
            f"| Content preview: {text[:100] if text else 'no text'} "
            f"| Attachment: {attachment_type or 'none'}"
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

    except TimeoutError:
        logger.error("Airtable query timed out in cmd_kek_push")
        await message.reply(
            "⏱ Service is temporarily slow. Please try again in a moment."
        )
        return None
    except Exception as e:
        logger.exception("Unexpected error in cmd_kek_push")
        await message.reply("❌ An unexpected error occurred. Please try again later.")
        return None


async def cmd_kek_add_no_reply(message: Message):
    return await message.reply("↪️ Кеки нужно предлагать реплаем на сообщение")


async def cmd_kek_add_non_mechmath(message: Message):
    return await message.reply("➡️ Кеки можно предлагать только в @mechmath")
