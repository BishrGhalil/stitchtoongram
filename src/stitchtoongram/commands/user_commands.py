import asyncio
from datetime import datetime
from random import randint

from telegram import Update
from telegram.ext import ContextTypes

from ..const import MAX_REPORTS
from ..const import PARSE_MODE
from ..const import TMP
from ..const import UPLOADS
from ..db import Chat
from ..db import Option
from ..db import User
from ..db import session
from ..drive_download import drive_download
from ..messages import help_msg_text
from ..messages import mention_user_msg
from ..messages import request_header_msg
from ..messages import request_msg_cmd
from ..messages import start_msg_text
from ..stitch import unzip_stitch
from .decorators import not_blocked
from .decorators import registered
from .pre_processing import formmatter


@not_blocked
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formmatter(start_msg_text, update),
        disable_web_page_preview=True,
        parse_mode=PARSE_MODE,
    )


@not_blocked
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formmatter(help_msg_text, update),
        disable_web_page_preview=True,
        parse_mode=PARSE_MODE,
    )


@not_blocked
@registered
async def my_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = session.query(User).where(User.telegram_id == update.effective_user.id)
    u = query.first()
    points = f"{u.points} point{' ' if u.points == 1 else 's'}"
    days_left = u.next_earning().days
    days_left_s = f"{days_left} day{' ' if days_left == 1 else 's'}"
    msg = f"<b>Your Points</b>\nvalue: {points}\navailable until: {days_left_s}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formmatter(msg, update),
        disable_web_page_preview=True,
        parse_mode=PARSE_MODE,
    )


@not_blocked
@registered
async def request_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = session.query(User).where(User.telegram_id == update.effective_user.id).first()

    if u.is_requesting:
        msgs = ["You already have opened a request.\nWe will contact you soon."]
        chat_id = update.effective_chat.id
    else:
        u.is_requesting = True
        session.add(u)
        session.commit()
        msg = "Your request has been submitted successfully.\nWe will contact you soon."

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=formmatter(msg, update),
            disable_web_page_preview=True,
            parse_mode=PARSE_MODE,
        )
        msgs = [
            f"{request_header_msg.format(title='REQUEST_POINTS')}",
            f"{request_msg_cmd('give_points',update.effective_user.id)}",
            f"Info\nusername: {update.effective_user.username}\nfullname: {update.effective_user.full_name}",
        ]
        chat_id = (
            session.query(Option).where(Option.name == "REQUESTS_CH").first().value
        )

    for msg in msgs:
        await context.bot.send_message(
            chat_id=chat_id,
            text=formmatter(msg, update),
            disable_web_page_preview=True,
            parse_mode=PARSE_MODE,
        )


@not_blocked
@registered
async def author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    author_id_op = str(
        session.query(Option).where(Option.name == "AUTHOR_TE_ID").first()
    )
    if not author_id_op:
        return

    author_id = author_id_op.value
    author_mention = mention_user_msg.format(name="Beshr Alghalil", id=author_id)
    msg = f"My Author: {author_mention}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formmatter(msg, update),
        disable_web_page_preview=True,
        parse_mode=PARSE_MODE,
    )


@not_blocked
@registered
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        msgs = [
            "<b>Faild: </b> Please provide a report message",
            "example: /report I have points but can't compress a file.",
        ]
        chat_id = update.effective_chat.id
    else:
        u = (
            session.query(User)
            .where(User.telegram_id == update.effective_user.id)
            .first()
        )
        if u.opened_reports > MAX_REPORTS:
            msgs = [f"Can't report more than {MAX_REPORTS} reports"]
            chat_id = update.effective_chat.id
        else:
            user_mention = mention_user_msg.format(
                name=update.effective_user.username, id=update.effective_user.id
            )
            msgs = [
                f"{user_mention}\n{' '.join(context.args)}",
                request_msg_cmd(
                    "reset_reports",
                    update.effective_user.id,
                ),
            ]
            u.opened_reports += 1
            session.add(u)
            session.commit()
            chat_id = (
                session.query(Option).where(Option.name == "REPORTS_CH").first().value
            )
    for msg in msgs:
        await context.bot.send_message(
            chat_id=chat_id,
            text=formmatter(msg, update),
            disable_web_page_preview=True,
            parse_mode=PARSE_MODE,
        )


@not_blocked
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = session.query(Chat).where(Chat.chat_id == update.effective_chat.id).first()
    u = u = (
        session.query(User).where(User.telegram_id == update.effective_user.id).first()
    )
    if not u:
        u = User(
            username=update.effective_user.username,
            telegram_id=update.effective_user.id,
            full_name=update.effective_user.full_name,
        )
        session.add(u)
        session.commit()
    if not c:
        c = Chat(user_id=u.id, chat_id=update.effective_chat.id)
        session.add(c)
        session.commit()
    if u.is_registered:
        msgs = ["You are already registered"]
        chat_id = update.effective_chat.id

    else:
        if u.is_requesting:
            msgs = ["You already have requested a registration please be patient."]
            chat_id = update.effective_chat.id
        else:
            msg = "Your request has been submitted"
            u.is_requesting = True
            session.add(u)
            session.commit()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=formmatter(msg, update),
                disable_web_page_preview=True,
                parse_mode=PARSE_MODE,
            )
            msgs = [
                request_header_msg.format(title="REGISTER"),
                request_msg_cmd(
                    "add_user",
                    update.effective_user.id,
                    update.effective_user.username,
                    update.effective_user.full_name.replace(" ", "_"),
                ),
            ]
            chat_id = (
                session.query(Option).where(Option.name == "REQUESTS_CH").first().value
            )
    for msg in msgs:
        await context.bot.send_message(
            chat_id=chat_id,
            text=formmatter(msg, update),
            disable_web_page_preview=True,
            parse_mode=PARSE_MODE,
        )


@not_blocked
async def all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Type /help to see all options"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formmatter(msg, update),
        disable_web_page_preview=True,
        parse_mode=PARSE_MODE,
    )


@not_blocked
@registered
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    quality = 80
    height = 10000
    out = TMP / datetime.now().strftime(f"%Y%M%d_%H%m%s{randint(10000, 99999)}")
    down_path = UPLOADS
    task = asyncio.create_task(
        drive_download(
            url,
            down_path,
            lambda z: unzip_stitch(z, quality, height, str(out)),
        )
    )

    processed = await task
    msg = "Your file is ready. Please wait for it to upload."
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=formmatter(msg, update),
        disable_web_page_preview=True,
        parse_mode=PARSE_MODE,
    )
