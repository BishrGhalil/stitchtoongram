import argparse
import json
import logging
import os
import subprocess

from telegram.ext import ApplicationBuilder

from stitchtoongram.commands import COMMANDS_HANDLERS
from stitchtoongram.const import TMP_DIRNAME
from stitchtoongram.const import UPLOADS_DIRNAME
from stitchtoongram.db import Option
from stitchtoongram.db import User
from stitchtoongram.db import session

logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.INFO)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def load_secrets():
    try:
        with open("secrets.json", "r") as fp:
            secrets = json.load(fp)
    except FileNotFoundError:
        logging.error(
            "`secrets.json` does not exists, please add this file and add the required secrets"
        )
        exit(1)
    else:
        return secrets


def commit_initial_data():
    try:
        with open("initial_db_data.json", "r") as fp:
            data = json.load(fp)

            for option in data["options"]:
                session.merge(Option(**option))

            for user in data["users"]:
                u = session.query(User).where(User.username == user["username"]).first()
                if not u:
                    session.add(User(**user))
                else:
                    id = u.id
                    u = User(**user)
                    u.id = id
                    session.merge(u)

            session.commit()
    except FileNotFoundError:
        logging.error(
            "`initial_db_data.json` does not exists, will continue with no initial data"
        )


def init_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--shell",
        help="Run interactive shell with associated imports",
        action="store_true",
    )

    return parser.parse_args()


def make_required_dirs():
    for _dir in (TMP_DIRNAME, UPLOADS_DIRNAME):
        os.makedirs(_dir, exist_ok=True)


if __name__ == "__main__":
    SECRETS = load_secrets()
    commit_initial_data()
    make_required_dirs()
    args = init_argparser()

    if args.shell:
        exit(subprocess.run(["python3", "-i", "src/stitchtoongram/shell.py"]))

    # adding secrets to db
    session.merge(
        Option(
            name="REQUESTS_CH", value=SECRETS["requests_channel_id"], data_type="int"
        )
    )
    session.merge(
        Option(name="LOGS_CH", value=SECRETS["logs_channel_id"], data_type="int")
    )
    session.merge(
        Option(name="REPORTS_CH", value=SECRETS["reports_channel_id"], data_type="int")
    )
    session.merge(
        Option(name="AUTHOR_TE_ID", value=SECRETS["author_id"], data_type="int")
    )
    session.commit()

    # registering handlers and starting application server
    application = ApplicationBuilder().token(SECRETS["bot_token"]).build()
    for ch in COMMANDS_HANDLERS:
        application.add_handler(ch)

    application.run_polling()
