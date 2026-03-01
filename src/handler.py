import logging
import pytz

from config.bot_text import BotText
from database.models import User
from datetime import datetime as dt
from enum import IntEnum, auto
from peewee import DoesNotExist
from telegram import Update, User as TelegramUser
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters)
from time import sleep

class State(IntEnum):
    INITIALIZE_DEADLINE = auto()
    INITIALIZE_GOALS = auto()
    VERIFY_GOALS = auto()
    EDIT_GOALS = auto()
    INITIALIZE_TIMEZONE = auto()
    CANCEL = auto()


# HELPER FUNCTIONS


async def get_user(telegram_user: TelegramUser) -> User:
    try:
        user = User.get(User.telegram_id == telegram_user.id)
        logging.info(f"User found. TelegramId: {user.telegram_id}")
    except DoesNotExist:
        user = None
        logging.info("No user found.")

    logging.debug(user)
    return user


def try_parse_date(date_str: str, format: str) -> str:
    try:
        d = dt.strptime(date_str, format)
    except ValueError:
        d = None
    
    return d


def format_goal_list(goals: list, user_data: dict) -> str:
    goal_str = ""
    for goal in goals:
        goal_str += str(goals.index(goal) + 1) + ". " + goal + "\n"
    deadline_str = dt.strftime(user_data["deadline"], "%m/%d/%Y")
    return BotText.verify_goals.format(deadline = deadline_str, goals = goal_str)


# COMMAND HANDLERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = State.CANCEL
    reply_text = ""

    await update.message.reply_text(BotText.welcome)

    user = await get_user(update.message.from_user)
    if user == None:
        # sleep(2)
        state = State.INITIALIZE_DEADLINE
        reply_text = BotText.initialize_deadline

    await update.message.reply_text(reply_text)
    return state


async def author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=BotText.author)


def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


# STATE HANDLERSI = au

async def initialize_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = State.CANCEL
    reply_text = ""
    user_data = context.user_data

    deadline = try_parse_date(update.message.text, "%m/%d/%Y")
    if deadline == None:
        state = State.INITIALIZE_DEADLINE
        reply_text = BotText.initialize_deadline_fail
    else:
        state = State.INITIALIZE_GOALS
        reply_text = BotText.initialize_goals
        user_data["deadline"] = deadline

    await update.message.reply_text(reply_text)
    return state


async def initialize_goals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = State.CANCEL
    reply_text = ""
    user_data = context.user_data

    goals = update.message.text.splitlines()
    if len(goals) < 6:
        state = State.INITIALIZE_GOALS
        reply_text = BotText.initialize_goals_fail
    else:
        state = State.VERIFY_GOALS
        reply_text = format_goal_list(goals, user_data)
        user_data["goals"] = goals

    await update.message.reply_text(reply_text)
    return state


async def edit_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = State.CANCEL
    reply_text = ""
    user_data = context.user_data
    
    state = State.VERIFY_GOALS
    goals = user_data["goals"]
    goals[user_data["edit_index"]] = update.message.text
    reply_text = format_goal_list(goals, user_data)
    
    await update.message.reply_text(reply_text)
    return state


async def verify_goals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = State.CANCEL
    reply_text = ""
    user_data = context.user_data
    
    user_choice = update.message.text
    logging.info(user_choice)
    if int(user_choice) == 0: 
        state = State.INITIALIZE_TIMEZONE
        reply_text = BotText.initialize_timezone
    else:
        state = State.EDIT_GOALS
        user_data["edit_index"] = int(user_choice) - 1
        reply_text = BotText.edit_goal.format(goal = user_data["goals"][int(user_choice) - 1])
    
    await update.message.reply_text(reply_text)
    return state


async def initialize_timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = State.CANCEL
    reply_text = ""
    user_data = context.user_data
    
    try:
        user_data["country_timezone"] = pytz.country_timezones(update.message.text)
        reply_text = BotText.finish_initialization
        state = ConversationHandler.END
    except:
        state = State.INITIALIZE_TIMEZONE
        reply_text = "That doesn't seem right. Check your typo and try again."
    
    await update.message.reply_text(reply_text)
    return state


conv = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        State.INITIALIZE_DEADLINE: [MessageHandler(None, initialize_deadline)],
        State.INITIALIZE_GOALS: [MessageHandler(None, initialize_goals)],
        State.VERIFY_GOALS: [MessageHandler(filters.Regex("^[0-6]$"), verify_goals)],
        State.EDIT_GOALS: [MessageHandler(None, edit_goal)],
        State.INITIALIZE_TIMEZONE: [MessageHandler(None, initialize_timezone)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)