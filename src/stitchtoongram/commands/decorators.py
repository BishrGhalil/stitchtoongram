from ..const import PARSE_MODE
from ..db import User
from ..db import session
from ..messages import admin_required_msg
from ..messages import notblocked_required_msg
from ..messages import register_required_msg
from .pre_processing import formmatter


def registered(fn):
    async def decorated(*args, **kwargs):
        u = (
            session.query(User)
            .where(User.telegram_id == args[0].effective_user.id)
            .first()
        )
        if not u or not u.is_registered:
            return await args[1].bot.send_message(
                chat_id=args[0].effective_chat.id,
                text=formmatter(register_required_msg, args[0]),
                disable_web_page_preview=True,
                parse_mode=PARSE_MODE,
            )
        else:
            return await fn(*args, **kwargs)

    return decorated


def not_blocked(fn):
    async def decorated(*args, **kwargs):
        u = (
            session.query(User)
            .where(User.telegram_id == args[0].effective_user.id)
            .first()
        )
        if u and u.is_blocked:
            return await args[1].bot.send_message(
                chat_id=args[0].effective_chat.id,
                text=formmatter(notblocked_required_msg, args[0]),
                disable_web_page_preview=True,
                parse_mode=PARSE_MODE,
            )
        else:
            return await fn(*args, **kwargs)

    return decorated


def admin(fn):
    async def decorated(*args, **kwargs):
        u = (
            session.query(User)
            .where(User.telegram_id == args[0].effective_user.id)
            .first()
        )
        if not u:
            return await args[1].bot.send_message(
                chat_id=args[0].effective_chat.id,
                text=formmatter(register_required_msg, args[0]),
                disable_web_page_preview=True,
                parse_mode=PARSE_MODE,
            )
        else:
            if not u.is_admin:
                return await args[1].bot.send_message(
                    chat_id=args[0].effective_chat.id,
                    text=formmatter(admin_required_msg, args[0]),
                    disable_web_page_preview=True,
                    parse_mode=PARSE_MODE,
                )
            else:
                return await fn(*args, **kwargs)

    return decorated
