# Telegram MarkdownV2 format https://core.telegram.org/bots/api#markdownv2-style

start_msg_text = """<b>Hey, @first @last!</b>
Welcome to <b>stitchtoongram</b> the <b>Telegram</b> bot for <a href="github.com/BishrGhalil/stitchtoon"><b>stitchtoon</b></a>
You can start by sending me a webtoon/manga zip file with max size of 150MB.
"""

help_msg_text = """<b>Help</b>
Just send a webtoon/manga zip file with max size of 150MB.

/author - author telegram account.
/help - shows this help message.
/my_points - your points.
/register - request a registeration.
/report - report an issue, args: message.
/request_points - request admins for more points.
/start - start message.
"""

admin_help_msg_text = """<b>Admin Help</b>

/add_user - add a user, args: telegram id, username, full name.
/admin_help - shows this help message.
/block - blocks a user from using the bot, args: id.
/give_points - award points to a specific user, args: telegram id, points.
/list_options - list options.
/list_users - list users.
/reset_reports - reset a user reports, args: telegram id.
/unblock - unblocks a user a blocked user, args: id.
/update_option - update option value, args: name, value.
/user_info - get user information.
"""

admin_required_msg = """<b>Failed:</b> This command requires admin role."""
register_required_msg = """<b>Failed:</b> You are not registered."""
notblocked_required_msg = """<b>Failed:</b> You are blocked from using this bot."""

request_header_msg = "[{title}]"

mention_user_msg = '<a href="tg://user?id={id}">{name}</a>'


def request_msg_cmd(cmd, *args):
    cmd = "/" + cmd
    for arg in args:
        cmd += " " + str(arg)
    return cmd
