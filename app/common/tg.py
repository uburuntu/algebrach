from aiogram.types import Chat, Message, TelegramObject, Update, User

from common.utils import one_liner


def user_info(user: User, sender_chat: Chat | None = None) -> str:
    if sender_chat:
        return chat_info(sender_chat)

    last_name = " " + user.last_name if user.last_name else ""
    username = ", @" + user.username if user.username else ""
    language_code = ", " + user.language_code if user.language_code else ""
    return f"{user.first_name}{last_name} ({user.id}{username}{language_code})"


def chat_info(chat: Chat) -> str:
    if chat.type == "private":
        return "private"

    username = ", @" + chat.username if chat.username else ""
    return f"{chat.type} | {chat.title} ({chat.id}{username})"


def message_info(message: Message) -> str:
    prefix = f"{message.message_id} | "
    if message.text:
        return prefix + one_liner(message.text, cut_len=50)
    return prefix + f"type: {message.content_type}"


def extract_file_id(message: Message) -> str | None:
    if message.animation:
        return message.animation.file_id
    if message.audio:
        return message.audio.file_id
    if message.document:
        return message.document.file_id
    if message.photo:
        return message.photo[-1].file_id
    if message.sticker:
        return message.sticker.file_id
    if message.video:
        return message.video.file_id
    if message.video_note:
        return message.video_note.file_id
    if message.voice:
        return message.voice.file_id
    return None


def decompose_update(
    update: Update,
) -> tuple[TelegramObject, User | None, Chat | None, Chat | None, str]:
    user, sender_chat, chat = None, None, None

    if f := update.message:
        user = f.from_user
        sender_chat = f.sender_chat
        chat = f.chat
        info = message_info(f)
    elif f := update.edited_message:
        user = f.from_user
        sender_chat = f.sender_chat
        chat = f.chat
        info = message_info(f) + " [edited]"
    elif f := update.channel_post:
        chat = f.chat
        info = message_info(f)
    elif f := update.edited_channel_post:
        chat = f.chat
        info = message_info(f) + " [edited]"
    elif f := update.inline_query:
        user = f.from_user
        info = one_liner(f.query, cut_len=50)
    elif f := update.chosen_inline_result:
        user = f.from_user
        info = one_liner(f.query, cut_len=50)
    elif f := update.callback_query:
        if f.message:
            chat = f.message.chat
        user = f.from_user
        info = f.data
    elif f := update.shipping_query:
        user = f.from_user
        info = f.as_json()
    elif f := update.pre_checkout_query:
        user = f.from_user
        info = f.as_json()
    elif f := update.poll:
        info = (
            f"{one_liner(f.question, cut_len=50)} ({f.id}),"
            f" {[o.text for o in f.options]}, {f.total_voter_count} voter(s)"
        )
    elif f := update.poll_answer:
        user = f.user
        info = f"{f.option_ids} ({f.poll_id})"
    elif f := (update.chat_member or update.my_chat_member):
        user = f.from_user
        chat = f.chat
        info = (
            f"{user_info(f.new_chat_member.user)}: {f.old_chat_member.status} ->"
            f" {f.new_chat_member.status}"
        )
    else:
        f = update
        info = update.as_json()

    return f, user, sender_chat, chat, info
