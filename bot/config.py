import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_dotenv():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8-sig") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


load_dotenv()

BOT_TOKEN = "".join((os.getenv("BOT_TOKEN", "")).split())
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID") or None
LEAD_SECRET = os.getenv("LEAD_SECRET") or None
BOT_WEB_HOST = os.getenv("BOT_WEB_HOST", "127.0.0.1")
BOT_WEB_PORT = int(os.getenv("BOT_WEB_PORT", "8080"))
DB_PATH = BASE_DIR / "leads.db"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
