"""Cautious visual screening of skin images through Groq's vision model."""

from __future__ import annotations

import base64
import io
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

load_dotenv(Path(__file__).resolve().parents[1] / "Telegram_bot" / ".env")

SCREENING_PROMPT = """You are a cautious AI visual-screening assistant for rural users.
Analyze ONLY visible skin findings in this photograph. This is not a diagnosis.
Accept only an image containing a visible wound, rash, or swelling. Reject unrelated,
normal, or unusable images. For accepted images describe only what is visible:
location, color, shape/distribution, bumps or blisters, crusting/scaling, open
skin/bleeding, discharge, and swelling. Never invent symptoms, duration, exposure,
age, or medical history.

Give exactly five possible explanations ordered by visual compatibility. For each
give a name, one-sentence description, visible evidence, and confidence (VERY LOW,
LOW, MODERATE, or HIGH). Never call anything confirmed or definite. Choose one
doctor priority: LOW, MEDIUM, or HIGH, with a brief reason. Select the most
visually compatible possibility and explain why. Do not prescribe treatment.

Use plain text, short sentences, and at most 350 words. For rejected images return
only Image check, Status, Reason, and Limitation. For accepted images use:
Image check / Status / Reason / What is visible / Five possible explanations (1-5)
/ Doctor priority / Most visually compatible possibility / Limitation.
State that this is AI visual screening only and not a medical diagnosis."""


def compress_image_to_base64(path: str | os.PathLike[str], max_dim: int = 1024) -> str:
    """Resize an image safely and return a JPEG data payload."""
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def analyze_image(image_path: str | os.PathLike[str]) -> str:
    """Return a visual screening report for ``image_path``."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it to Telegram_bot/.env to use photo analysis."
        )

    try:
        # Import lazily so text-only bot users do not need to initialize Groq.
        from groq import Groq
    except ImportError as error:
        raise RuntimeError(
            "The Groq image dependencies are missing. Install "
            "Telegram_bot/requirements.txt in the interpreter running the bot."
        ) from error

    image_data = compress_image_to_base64(image_path)
    request = {
        "model": os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b").strip(),
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SCREENING_PROMPT},
                    {"type": "image_url", "image_url": {
                        "url": "data:image/jpeg;base64," + image_data
                    }},
                ],
            }
        ],
        "temperature": 0.2,
        "max_completion_tokens": 800,
    }

    client = Groq(api_key=api_key)
    for attempt in range(3):
        try:
            response = client.chat.completions.create(**request)
            break
        except Exception as error:
            status_code = getattr(error, "status_code", None)
            retryable = status_code == 429 or status_code is None or status_code >= 500
            if not retryable or attempt == 2:
                raise
            time.sleep(2 ** attempt)
    report = response.choices[0].message.content
    if not report or not report.strip():
        raise RuntimeError("The image model returned an empty report.")
    return report.strip()
