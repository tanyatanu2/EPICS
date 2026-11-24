import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path

from telegram import Update
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
from Telegram_bot.config import (
    GROQ_API_KEY,
    TELEGRAM_TOKEN,
    validate_config
)

from sr_ts.sr_ts import process_audio_pipeline

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to the AI Healthcare Assistant!\n\n"
        "You can interact with me using:\n\n"
        "💬 Text messages - Describe your symptoms.\n"
        "📷 Photos - Upload an image of your skin concern.\n"
        "🎤 Voice notes - Explain your symptoms through voice.\n\n"
        "I will automatically identify your input type "
        "and process it accordingly.\n\n"
        "⚠️ This system provides preliminary health information, "
        "not a medical diagnosis. Please visit a doctor "
        "for proper evaluation and treatment."
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if not user_text or not user_text.strip():
        return

    try:
        await update.message.reply_text("Processing your message...")

        # Send text to AI model
        ai_reply = await asyncio.to_thread(
            get_ai_response,
            user_text.strip()
        )

        # Return AI response
        await update.message.reply_text(str(ai_reply))

    except Exception as error:
        logger.exception("Text processing failed: %s", error)
        await update.message.reply_text(
            "Something went wrong while processing your message. "
            "Please try again."
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    if not GROQ_API_KEY:
        await update.message.reply_text(
            "Photo analysis is not configured. "
            "Please configure GROQ_API_KEY."
        )
        return

    await update.message.reply_text("📷 Image received. Analyzing your image...")

    try:
        with tempfile.TemporaryDirectory(prefix="epics-photo-", ignore_cleanup_errors=True) as temp_dir:
            telegram_file = await context.bot.get_file(
                update.message.photo[-1].file_id
            )
            image_path = os.path.join(temp_dir, "image.jpg")
            await telegram_file.download_to_drive(image_path)

            if not os.path.isfile(image_path) or os.path.getsize(image_path) == 0:
                raise RuntimeError("Downloaded image is empty.")

            # Send image to image analysis backend
            report = await asyncio.to_thread(analyze_image, image_path)

        await update.message.reply_text(str(report))

    except Exception as error:
        logger.exception("Photo analysis failed: %s", error)
        await update.message.reply_text(
            "Unable to analyze your image. "
            "Please send a clear, well-lit photo and try again."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.voice:
        return

    voice = update.message.voice
    await update.message.reply_text("🎤 Voice message received. Processing...")

    try:
        # Fixed: ignore_cleanup_errors must be passed as an argument to TemporaryDirectory
        with tempfile.TemporaryDirectory(prefix="epics-voice-", ignore_cleanup_errors=True) as temp_dir:
            telegram_file = await context.bot.get_file(voice.file_id)
            audio_path = os.path.join(temp_dir, "voice.ogg")
            
            await telegram_file.download_to_drive(audio_path)

            if not os.path.isfile(audio_path) or os.path.getsize(audio_path) == 0:
                raise RuntimeError("Downloaded voice file is empty.")

            # 1. Convert voice to text using your untouched sr_ts module
            transcription_result = await asyncio.to_thread(process_audio_pipeline, audio_path)
            
            # If your pipeline returns a tuple (e.g., path_to_audio, text), extract just the text. 
            # If it just returns a string, this will handle it perfectly too.
            if isinstance(transcription_result, tuple):
                user_text = transcription_result[-1] 
            else:
                user_text = str(transcription_result)

            # 2. Pass the transcribed text into the AI model
            ai_reply = await asyncio.to_thread(get_ai_response, user_text)

            # 3. Send only the text response back to the user
            await update.message.reply_text(str(ai_reply))

    except Exception as error:
        logger.exception("Voice processing failed: %s", error)
        await update.message.reply_text(
            "Unable to process your voice message. Please try again."
        )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.audio:
        return

    audio = update.message.audio
    await update.message.reply_text("🎵 Audio file received. Processing...")

    try:
        # Fixed: Added ignore_cleanup_errors here as well
        with tempfile.TemporaryDirectory(prefix="epics-audio-", ignore_cleanup_errors=True) as temp_dir:
            telegram_file = await context.bot.get_file(audio.file_id)
            extension = Path(audio.file_name or "audio.mp3").suffix or ".mp3"
            audio_path = os.path.join(temp_dir, f"audio{extension}")
            
            await telegram_file.download_to_drive(audio_path)

            # 1. Process audio to get text
            transcription_result = await asyncio.to_thread(process_audio_pipeline, audio_path)
            
            if isinstance(transcription_result, tuple):
                user_text = transcription_result[-1] 
            else:
                user_text = str(transcription_result)

            # 2. Get AI response based on the transcribed text
            ai_reply = await asyncio.to_thread(get_ai_response, user_text)

            # 3. Send text reply back to user
            await update.message.reply_text(str(ai_reply))

    except Exception as error:
        logger.exception("Audio processing failed: %s", error)
        await update.message.reply_text(
            "Unable to process your audio file. Please try again."
        )

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please send a text message, photo, or voice note."
    )

def main():
    validate_config()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram AI Healthcare Bot is running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(f"Startup error: {error}") from error