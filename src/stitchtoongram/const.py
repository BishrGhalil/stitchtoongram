from pathlib import Path

from telegram.constants import ParseMode

PARSE_MODE = ParseMode.HTML
DB_NAME = "stitchtoongram.db"
MAX_REPORTS = 3
# TODOOO: make this directories when server starts
UPLOADS_DIRNAME = "uploads"
UPLOADS = Path(__file__).parent.parent.parent / UPLOADS_DIRNAME
TMP_DIRNAME = "tmp"
TMP = Path(__file__).parent.parent.parent / TMP_DIRNAME
