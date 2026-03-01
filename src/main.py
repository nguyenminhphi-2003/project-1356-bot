from config import *
from database import initialize_database
from handler import author, conv

from telegram.ext import ApplicationBuilder, CommandHandler

if __name__ == '__main__':
    initialize_database(config.DB_NAME)
    
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    author_handler = CommandHandler("author", author)

    application.add_handler(conv)
    application.add_handler(author_handler)

    application.run_polling()
