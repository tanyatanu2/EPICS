"""Configuration loaded from environment variables.

Copy ``.env.example`` to ``.env`` and add your own token, or set the values in
your operating system before starting the bot.  Secrets must never be committed
to source control.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(Path(__file__).with_name(".env"), override=False)


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b").strip()


def validate_config() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError(
            "TELEGRAM_TOKEN is not set. Copy .env.example to .env, add a new "
            "token from @BotFather, then start the bot again."
        )
