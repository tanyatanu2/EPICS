from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8659972313:AAETV315Stlef7VN5PFxs5Xi-pxzhOYttQo"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot ")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()