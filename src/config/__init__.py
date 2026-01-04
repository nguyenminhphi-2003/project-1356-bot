import logging

from dotenv import load_dotenv

load_dotenv()

from config.config import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)