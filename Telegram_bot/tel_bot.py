import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from Telegram_bot.ai_model import get_ai_response
from Telegram_bot.config import GROQ_API_KEY, TELEGRAM_TOKEN, validate_config

from ImageProcessing.imageprocessing import analyze_image

user_mode = {}
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Chat", "Photo", "Voice"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Select mode:",
        reply_markup=reply_markup
    )


async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = update.message.text.lower()
    user_id = update.message.from_user.id

    if mode in ["chat", "photo", "voice"]:
        user_mode[user_id] = mode
        prompt = (
            "Please send a clear photo of the skin concern."
            if mode == "photo"
            else "Please provide the symptoms."
        )
        await update.message.reply_text(
            f"{mode.capitalize()} mode activated.\n{prompt}"
        )
    else:
        await update.message.reply_text("Please select a valid mode.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mode = user_mode.get(user_id, "chat")  # default chat


    if mode == "chat":
        user_text = update.message.text
        if not user_text or not user_text.strip():
            await update.message.reply_text("Please describe your symptoms in text.")
            return
        # requests is synchronous; use a worker thread so polling stays responsive.
        ai_reply = await asyncio.to_thread(get_ai_response, user_text.strip())
        await update.message.reply_text(ai_reply)

    elif mode == "photo":
        await update.message.reply_text("Please send a clear photo of the skin concern.")

    elif mode == "voice":
        await update.message.reply_text("Voice feature not implemented yet.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download and analyze the highest-resolution Telegram photo."""
    if not update.message or not update.message.photo:
        return
    if not GROQ_API_KEY:
        await update.message.reply_text(
            "Photo analysis is not configured. Add GROQ_API_KEY to Telegram_bot/.env."
        )
        return

    await update.message.reply_text(
        "I’m reviewing the image. This is visual screening, not a diagnosis."
    )
    try:
        with tempfile.TemporaryDirectory(prefix="epics-photo-") as temp_dir:
            telegram_file = await context.bot.get_file(
                update.message.photo[-1].file_id
            )
            image_path = os.path.join(temp_dir, "image.jpg")
            await telegram_file.download_to_drive(image_path)
            if not os.path.isfile(image_path) or os.path.getsize(image_path) == 0:
                raise RuntimeError("Telegram returned an empty image file.")
            report = await asyncio.to_thread(analyze_image, image_path)
        await update.message.reply_text(report)
    except Exception as error:
        logging.getLogger(__name__).exception(
            "Photo analysis failed for Telegram photo: %s", error
        )
        await update.message.reply_text(
            "I couldn’t analyze that image. Please send a clear, well-lit photo and try again."
        )


def main():
    validate_config()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex("^(Chat|Photo|Voice)$"),
        set_mode
    ))


    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    print("Bot running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(f"Startup error: {error}") from error
