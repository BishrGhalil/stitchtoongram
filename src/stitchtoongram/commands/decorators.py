import functools
import logging
import re

from ..const import PARSE_MODE
from ..db import User
from ..db import session
from ..messages import admin_required_msg
from ..messages import notblocked_required_msg
from ..messages import register_required_msg
from .pre_processing import args_parser
from .pre_processing import formmatter
from .pre_processing import send_message


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


def context_validate(func=None, *, format: str):
    def decorator_validate_format(func):
        @functools.wraps(func)
        async def wrapper_validate_format(*args, **kwargs):
            # context.args
            update = args[0]
            context = args[1]
            usage = f"usage: /{func.__name__} {format}".replace("<", "&lt;").replace(
                ">", "&gt;"
            )

            message = update.message.text
            context_args = args_parser(message)

            params = re.findall("(<([a-zA-Z]*):(str|int|float|bool)>)", format)

            if params and not context_args or len(context_args) != len(params):
                msgs = [
                    "<b>Faild: </b>invalid args.",
                    usage,
                    "If you are providing strings with white spaces, make sure to use double quotes.",
                ]
                for msg in msgs:
                    await send_message(context, update, update.effective_chat.id, msg)

            else:
                data_types = {
                    int.__name__: int,
                    str.__name__: str,
                    float.__name__: float,
                    bool.__name__: bool,
                }

                msgs = []
                for i, arg in enumerate(context_args):
                    try:
                        if params[i][2] != "any":
                            data_types[params[i][2]](arg)
                    except KeyError:
                        logging.error(f"Invalid datatype {params[i][2]}")
                    except ValueError:
                        msgs.append(
                            f"<b>Faild: </b>{params[i][1]} should be of type {params[i][2]}"
                        )
                        msgs.append(usage)
                        for msg in msgs:
                            await send_message(
                                context, update, update.effective_chat.id, msg
                            )
                        return
                return await func(*args, **kwargs)

        return wrapper_validate_format

    if func is None:
        return decorator_validate_format
    return decorator_validate_format(func)
