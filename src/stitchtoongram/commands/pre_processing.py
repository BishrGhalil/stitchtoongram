from telegram import Update


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
