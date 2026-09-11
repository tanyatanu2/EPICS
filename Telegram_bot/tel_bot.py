from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from config import TELEGRAM_TOKEN
from ai_model import get_ai_response

user_mode = {}


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
        await update.message.reply_text(f"{mode.capitalize()} mode activated.\nPlease provide the symptoms.")
    else:
        await update.message.reply_text("Please select a valid mode.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mode = user_mode.get(user_id, "chat")  # default chat


    if mode == "chat":
        user_text = update.message.text
        ai_reply = get_ai_response(user_text)
        await update.message.reply_text(ai_reply)

    elif mode == "photo":
        await update.message.reply_text("Image feature not implemented yet.")

    elif mode == "voice":
        await update.message.reply_text("Voice feature not implemented yet.")


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex("^(Chat|Photo|Voice)$"),
        set_mode
    ))


    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()