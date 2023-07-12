import re

from telegram import Update

from ..const import PARSE_MODE


def formmatter(text, update: Update = None):
    if update is None:
        return text
    formats = (
        ("@username", update.effective_user.username),
        ("@first", update.effective_user.first_name),
        ("@last", update.effective_user.last_name),
        ("@full_name", update.effective_user.full_name),
        ("@chat_id", update.effective_chat.id),
        ("@user_id", update.effective_user.id),
    )
    for fm in formats:
        text = text.replace(fm[0], str(fm[1]))

    return text


def args_parser(message):
    message = re.sub(f"/[a-zA-Z_]*", "", message).strip().replace("\\", "")
    args = re.findall(r'"[^"]*"|\S+', message)
    args = [s.strip('"') for s in args]

    return args


async def send_message(
    context, update, chat_id, msg, parse_mode=PARSE_MODE, notify=True
):
    return await context.bot.send_message(
        chat_id=chat_id,
        text=formmatter(msg, update),
        disable_web_page_preview=True,
        parse_mode=parse_mode,
        disable_notification=not notify,
    )
