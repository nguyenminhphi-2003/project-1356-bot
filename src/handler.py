import logging
import pytz

from config.bot_text import BotText
from database.models import User, Goal, Deadline
from datetime import datetime, time
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = State.CANCEL
    reply_text = ""


    user = await get_user(update.message.from_user)
    if user == None:
        await update.message.reply_text(BotText.welcome)
        sleep(2)
        state = State.INITIALIZE_DEADLINE
        reply_text = BotText.initialize_deadline
    else:
        goal_list = []
        for goal in Goal.select(Goal, User).join(User).iterator():
            goal_list.append(goal.name)
            
        state = ConversationHandler.END
        reply_text = BotText.existed_user_message.format(goals = list_to_bulleted_string(goal_list))
            

    await update.message.reply_text(reply_text)
    return state


async def author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=BotText.author)


def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


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

    logging.info(user_data)
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
        
        save_user(update=update,user_data=user_data)
        send_time = time(hour=7, minute=0, second=0, microsecond=0, tzinfo=pytz.timezone(user_data["country_timezone"][0]), fold=1)
        context.job_queue.run_once(remind,when=1.5,chat_id=update.effective_message.chat_id,data=user_data)
        context.job_queue.run_daily(remind, time=send_time,chat_id=update.effective_message.chat_id,data=user_data)
        
        state = ConversationHandler.END
    except Exception as e: 
        logging.error(e)
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


async def get_user(telegram_user: TelegramUser) -> User:
    try:
        user = User.get(User.telegram_id == telegram_user.id)
        logging.info(f"User found. TelegramId: {user.telegram_id}")
    except DoesNotExist:
        user = None
        logging.info("No user found.")

    logging.debug(user)
    return user


async def remind(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    user_data = job.data
    
    goal_str = ""
    for goal in user_data["goals"]:
        goal_str += f"    {user_data['goals'].index(goal) + 1}. {goal}\n"
    deadline_str = parse_datetime_to_string(user_data["deadline"])
    
    text = BotText.daily_remind.format(
        days=(user_data["deadline"] - datetime.now()).days,
        deadline = deadline_str,
        goals = goal_str)
    
    await context.bot.send_message(text=text, chat_id=job.chat_id)


def try_parse_date(date_str: str, format: str) -> str:
    try:
        d = datetime.strptime(date_str, format)
    except ValueError:
        d = None
    
    return d


def format_goal_list(goals: list, user_data: dict) -> str:
    return BotText.verify_goals.format(
        deadline = parse_datetime_to_string(user_data["deadline"]),
        goals = list_to_bulleted_string(goals)
    )


def list_to_bulleted_string(list: list) -> str:
    result = ""
    for list_item in list:
        result += str(list.index(list_item) + 1) + ". " + list_item + "\n"
    return result


def parse_datetime_to_string(dt: datetime) -> str:
    return datetime.strftime(dt, "%m/%d/%Y")
    

def save_user(update: Update, user_data: dict) -> None:
    user = User.create(username=update.message.from_user.name, telegram_id=update.message.from_user.id, chat_id=update.message.chat_id)
    Deadline.create(deadline=user_data["deadline"], country_timezone=user_data["country_timezone"], user=user)
    for goal_string in user_data["goals"]:
        Goal.create(name=goal_string,user=user)