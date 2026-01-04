from config.bot_text import BotText
from telegram import Update
from telegram.ext import ContextTypes

class Handler():
    
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=BotText.welcome)

    async def author(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=BotText.author)