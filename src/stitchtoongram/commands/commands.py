from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from .admin_commands import add_user
from .admin_commands import admin_help
from .admin_commands import block
from .admin_commands import give_points
from .admin_commands import list_options
from .admin_commands import list_users
from .admin_commands import reset_reports
from .admin_commands import unblock
from .admin_commands import update_option
from .admin_commands import user_info
from .user_commands import all_messages
from .user_commands import author
from .user_commands import download
from .user_commands import help
from .user_commands import my_points
from .user_commands import register
from .user_commands import report
from .user_commands import request_points
from .user_commands import start

COMMANDS_HANDLERS = (
    CommandHandler("add_user", add_user),
    CommandHandler("admin_help", admin_help),
    CommandHandler("author", author),
    CommandHandler("block", block),
    CommandHandler("give_points", give_points),
    CommandHandler("help", help),
    CommandHandler("list_options", list_options),
    CommandHandler("list_users", list_users),
    CommandHandler("my_points", my_points),
    CommandHandler("register", register),
    CommandHandler("report", report),
    CommandHandler("request_points", request_points),
    CommandHandler("reset_reports", reset_reports),
    CommandHandler("start", start),
    CommandHandler("unblock", unblock),
    CommandHandler("update_option", update_option),
    CommandHandler("user_info", user_info),
    MessageHandler(filters.ATTACHMENT, download),
    MessageHandler(filters.TEXT & filters.COMMAND, all_messages),
)
