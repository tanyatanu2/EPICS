# Telegram Health Assistant

## Run it locally

1. Install Python 3.10 or newer.
2. From the repository root, install all dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Install and start [Ollama](https://ollama.com), then download the model:

   ```bash
   ollama pull llama3.2
   ```

4. Create the root `.env` file, then replace the placeholder with a **new**
   token from Telegram's `@BotFather`. The token that was previously in this
   repository has been exposed and should be revoked in `@BotFather`.
5. Start the bot from the repository root:

   ```bash
   .venv/bin/python -m Telegram_bot.tel_bot
   ```

The bot starts in chat mode. Send `/start`, choose a mode, then send symptoms.
