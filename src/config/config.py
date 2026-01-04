import logging
import os

from dotenv import load_dotenv


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


load_dotenv()


BOT_TOKEN = os.environ.get("BOT_TOKEN")
