import logging
import random

from aiogram.types import Message
from airtable.kek_storage import kek_storage
from common.tg import extract_attachment_file_id, reply_with_attachment
from settings import config

logger = logging.getLogger(__name__)


async def cmd_kek(message: Message):
    """
    Handle /kek command - return a random kek from storage.

    Args:
        message: Incoming Telegram message

    Returns:
        Sent message object or None on error
    """
    try:
        keks = await kek_storage.async_all()

        if not keks:
            await message.reply(
                "😔 No keks available at the moment. Please try again later!"
            )
            return None

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
                    try:
                        await kek_storage.async_update_file_id(kek["id"], file_id)
                    except Exception as e:
                        # Log but don't fail the request if file_id update fails
                        logger.warning(f"Failed to update file_id: {e}")

        return reply

    except TimeoutError:
        logger.error("Airtable query timed out in cmd_kek")
        await message.reply(
            "⏱ Service is temporarily slow. Please try again in a moment."
        )
        return None
    except Exception as e:
        logger.exception("Unexpected error in cmd_kek")
        await message.reply("❌ An unexpected error occurred. Please try again later.")
        return None
