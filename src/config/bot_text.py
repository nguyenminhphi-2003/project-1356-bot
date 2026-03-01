class BotText:
    welcome = """
    Welcome to Project 1356! 🚀
Inspired by Armin Mehdiz, this bot helps remind you of your goals every day.
Let's get started!"""

    author = """
    Author: Nguyễn Minh Phi 
Email: nmphi2710@gmail.com
Github: https://github.com/nguyenminhphi-2003"""

    review_goals = """
    Here are your goals until {deadline}:
{goals}
"""
  
    initialize_deadline = """
First, let's set an end date.
What date would you like to set as the deadline?

Please enter the date in MM/dd/YYYY format.
Example: 02/18/2029
"""

    initialize_deadline_fail = """
The date doesn't look right.

Please use the MM/DD/YYYY format.
Example: 02/18/2029
"""

    initialize_goals = """
Great! It's time set our goals.

Write all 6 goals in one message, with each goal on a separate line.
"""

    initialize_goals_fail = """
You need to specify exact 6 goals.

Write all 6 goals in one message, with each goal on a separate line.
"""

    verify_goals = """
Take a moment to review your goals.

If you'd like to change anything, just mention the goal number and what'd you like to change.
Or simply type '0' to move forward.

You can retype your choice if you make any mistakes.

Here are your goals until {deadline}:
{goals}
"""

    edit_goal = """
Please retype your goal below.

Your current version is:
    - {goal}
"""

    initialize_timezone = """
Last step! Please provide your timezone.

The bot will send you a reminder every day at 7:00 AM in your local time.

You can search for your country key here:
https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

Example: VN for Asia/Ho_Chi_Minh
"""

    finish_initialization = """
All set! 🎉

From now on, this bot will remind you of your goals every day.

Success is built quietly — keep building.

You can review your goals anytime by typing /review_goals.
"""