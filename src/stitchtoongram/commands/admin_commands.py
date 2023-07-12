from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..db import Chat
from ..db import Option
from ..db import User
from ..db import session
from ..messages import admin_help_msg_text
from .decorators import admin
from .decorators import context_validate
from .pre_processing import args_parser
from .pre_processing import send_message


@admin
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(context, update, update.effective_chat.id, admin_help_msg_text)


@admin
async def available_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


@admin
@context_validate(format="<id:int> <points:int>")
async def give_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    id = int(args[0])
    points = int(args[1])

    u = session.query(User).where(User.telegram_id == id).first()
    if not u:
        msg = "User not found."

    elif not u.is_registered:
        msg = "User not registered"

    else:
        c = session.query(Chat).where(Chat.user_id == u.id).first()
        if not c:
            msg = "No chat associated with this user\nPoints are not added."
        else:
            u.add_points(points)
            u.is_requesting = False
            session.add(u)
            session.commit()
            msg = f"Points added to {u.telegram_id} {u.full_name}"
            user_msg = f"<b>Hey @first</b>\nYou have granted <b>{points} point{'' if points == 1 else 's'}</b>."
            await send_message(context, update, c.chat_id, user_msg)

        await send_message(context, update, update.effective_chat.id, msg)


@admin
@context_validate(format="<id:int>")
async def reset_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    id = args[0]
    u = session.query(User).where(User.telegram_id == id).first()
    if not u:
        msg = "User not found."

    elif not u.is_registered:
        msg = "User not registered"

    else:
        c = session.query(Chat).where(Chat.user_id == u.id).first()
        if not c:
            msg = "No chat associated with this user\nNo changes have been made."
        else:
            u.opened_reports = 0
            session.add(u)
            session.commit()
            msg = f"Reports reseted to {u.telegram_id} {u.full_name}"
            user_msg = "<b>Hey @first</b>\nYour reports have been reseted."
            await send_message(context, update, c.chat_id, user_msg)

    await send_message(context, update, update.effective_chat.id, msg)


@admin
@context_validate(format="<id:int> <username:str> <fullname:str>")
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    id = int(args[0])
    username = args[1]
    full_name = args[2]
    u = session.query(User).where(User.telegram_id == id).first()
    if not u:
        u = User(
            username=username,
            telegram_id=id,
            full_name=full_name,
        )
        session.add(u)
        session.commit()
    if u.is_registered:
        msg = "User already registered"
    else:
        msg = "User has been added."
        u.is_registered = True
        u.is_requesting = False
        session.add(u)
        c = session.query(Chat).where(Chat.user_id == u.id).first()
        if c:
            user_msg = "<b>Good news for you @first</b>\nYou have been registered to use this bot."
            await send_message(context, update, c.chat_id, user_msg)
        else:
            msg = "No chat associated with this user."

    await send_message(context, update, update.effective_chat.id, msg)


@admin
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = session.query(User).all()

    data = [[f"<b>{'id':5}</b>", "<b>Name</b>"]]
    for user in users:
        data.append([user.id, user.full_name])

    msg = "<pre>"
    for i in data:
        msg += f"{str(i[0]):5} | {str(i[1])}\n"

    msg += "</pre>"

    await send_message(context, update, update.effective_chat.id, msg)


@admin
@context_validate(format="<id:int>")
async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    id = args[0]
    u = session.query(User).where(User.id == id).first()
    if not u:
        u = session.query(User).where(User.telegram_id == id).first()
    if not u:
        msg = "User not found."
    else:
        msg = (
            "<b>User Info</b>\n"
            f"<b>id:</b> {u.id}\n"
            f"<b>username:</b> {u.username}\n"
            f"<b>full name:</b> {u.full_name}\n"
            f"<b>telegram id:</b> {u.telegram_id}\n"
            f"<b>points:</b> {u.points}\n"
            f"<b>is admin:</b> {u.is_admin}\n"
            f"<b>is blocked:</b> {u.is_blocked}\n"
            f"<b>is requesting:</b> {u.is_requesting}\n"
            f"<b>points earned at:</b> {u.points_earned_at}\n"
            f"<b>next earning:</b> {u.next_earning()}\n"
            f"<b>joined at:</b> {u.created_at}\n"
        )
    await send_message(context, update, update.effective_chat.id, msg)


@admin
@context_validate(format="<id:int>")
async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    id = int(args[0])
    u = session.query(User).where(User.id == id).first()
    if not u:
        u = session.query(User).where(User.telegram_id == id).first()
    if not u:
        msg = "User not found."
    else:
        msg = "User has been blocked."
        u.is_blocked = True
        session.add(u)
        session.commit()

    await send_message(context, update, update.effective_chat.id, msg)


@admin
@context_validate(format="<id:int>")
async def unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    id = int(args[0])
    u = session.query(User).where(User.id == id).first()
    if not u:
        u = session.query(User).where(User.telegram_id == id).first()
    if not u:
        msg = "User not found."
    else:
        if not u.is_blocked:
            msg = "User is not unblocked."
        else:
            msg = "User has been unblocked."
            u.is_blocked = False
            session.add(u)
            session.commit()

    await send_message(context, update, update.effective_chat.id, msg)


@admin
async def list_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = session.query(Option).all()

    data = [[f"<b>{'Name':15}</b>", f"<b>{'Value':30}</b>"]]
    for option in options:
        data.append([option.name, option.value, option.data_type])

    msg = "<pre>"
    for i in data:
        msg += f"{str(i[0]):15} | {str(i[1]):30}\n"

    msg += "</pre>"

    await send_message(context, update, update.effective_chat.id, msg)


@admin
@context_validate(format="<name:str> <value:any>")
async def update_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    name = args[0]
    value = args[1]
    op = session.query(Option).where(Option.name == name).first()
    if not op:
        msg = "Option does not exists."
    else:
        cnvrtr = str
        if op.data_type == "int":
            cnvrtr = int
        elif op.data_type == "float":
            cnvrtr = float

        try:
            value = cnvrtr(value)
        except ValueError:
            msg = f"This is not a valid {op.type} type"
        else:
            op.value = value
            session.add(op)
            session.commit()
            msg = "Option has been updated."

    await send_message(context, update, update.effective_chat.id, msg)


@admin
@context_validate(format="<message:str>")
async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = args_parser(update.message.text)
    msg = args[0]
    chats = session.query(Chat).all()
    if chats:
        for chat in chats:
            await send_message(
                context, update, chat.chat_id, msg, parse_mode=ParseMode.MARKDOWN_V2
            )
