from config.config import BOT_TOKEN
from handler import Handler
from telegram.ext import ApplicationBuilder, CommandHandler

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', Handler.start)
    author_handler = CommandHandler('author', Handler.author)
    
    application.add_handler(start_handler)
    application.add_handler(author_handler)
    
    application.run_polling()