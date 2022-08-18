import asyncio
import importlib
import re
from contextlib import closing, suppress
from uvloop import install

from pyrogram import errors
from pyrogram import filters, idle,Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Maxrobot import app,LOG_GROUP_ID,BOT_USERNAME,bot,BOT_NAME,aiohttpsession
from Maxrobot.plugins import ALL_MODULES
from Maxrobot.utils import paginate_modules
from lang import get_command
from Maxrobot.utils.lang import language,languageCB
#from Maxrobot.utils.commands import *
# from Maxrobot.mongo.rulesdb import *
from Maxrobot.utils.start import get_private_rules,get_learn
#from Maxrobot.utils.kbhelpers import *
from Maxrobot.mongo.usersdb import adds_served_user,add_served_user
from Maxrobot.mongo.restart import clean_restart_stage
from Maxrobot.mongo.chatsdb import add_served_chat
from Maxrobot.plugins.fsub import ForceSub
from config import *
loop = asyncio.get_event_loop()
flood = {}

START_COMMAND = get_command("START_COMMAND")
HELP_COMMAND = get_command("HELP_COMMAND")
HELPABLE = {}

async def start_bot():
    global HELPABLE
    for module in ALL_MODULES:
        imported_module = importlib.import_module("Maxrobot.plugins." + module)
        if (
            hasattr(imported_module, "__MODULE__")
            and imported_module.__MODULE__
        ):
            imported_module.__MODULE__ = imported_module.__MODULE__
            if (
                hasattr(imported_module, "__HELP__")
                and imported_module.__HELP__
            ):
                HELPABLE[
                    imported_module.__MODULE__.replace(" ", "_").lower()
                ] = imported_module
    all_module = ""
    j = 1
    for i in ALL_MODULES:
        if j == 1:
            all_module += "•≫ Successfully imported:{:<15}.py\n".format(i)
            j = 0
        else:
            all_module += "•≫ Successfully imported:{:<15}.py".format(i)
        j += 1           
    restart_data = await clean_restart_stage()
    try:
        if restart_data:
            await app.edit_message_text(
                restart_data["chat_id"],
                restart_data["message_id"],
                "**Restarted Successfully**",
            )

        else:
            await app.send_message(LOG_GROUP_ID, "Bot started!")
    except Exception:
        pass
    print(f"{all_module}")
    print("""
 _____________________________________________   
|                                             |  
|          Deployed Successfully              |  
|         (C) 2021-2022 by @Theteambots        | 
|          Greetings from supun  :)           |
|_____________________________________________|""")
    await idle()
    await aiohttpsession.close()
    await app.stop()
    for task in asyncio.all_tasks():
        task.cancel() 



home_keyboard_pm = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text=" ➕ Add Me To Your Group ➕ ",url=f"http://t.me/{BOT_USERNAME}?startgroup=new",)],
    [InlineKeyboardButton(text="👩‍💻Support Chat", url=f"https://t.me/MaxRobotSupport"),
    InlineKeyboardButton(text="📢News Channel", url=f"https://t.me/MaxRobot_updates")],
    [InlineKeyboardButton(text="🔧Help🔧", callback_data="bot_commands")],
    [InlineKeyboardButton(text="🧬languages ", callback_data="langus")]])

keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="📚 Commands & help", url=f"t.me/{BOT_USERNAME}?start=help")]])

@app.on_message(filters.command(START_COMMAND))
@language
async def start(client, message: Message, _):
    chat_id = message.chat.id
    #User can't see start message without join channel...

    FSub = await ForceSub(bot, message)
    if FSub == 400:
        return
    #If user start bot on chat(group) this will display
    if message.chat.type != "private":
        await message.reply(_["main2"], reply_markup=keyboard)
        await adds_served_user(chat_id)     
        return await add_served_chat(chat_id) 

    if len(message.text.split()) > 1:

        name = (message.text.split(None, 1)[1]).lower()

        if name.startswith("rules"):
                return await get_private_rules(app, message, name)
                     
        if name.startswith("learn"):
                return await get_learn(app, message, name)
             
        if "_" in name:
            module = name.split("_", 1)[1]
            text = (_["main6"].format({HELPABLE[module].__MODULE__}
                + HELPABLE[module].__HELP__)
            )
            await message.reply(text, disable_web_page_preview=True)

        if name == "help":
            text, keyb = await help_parser(message.from_user.first_name)
            await message.reply(_["main5"],reply_markup=keyb, disable_web_page_preview=True)

        if name == "connections":
            await message.reply("** Run /connections to view or disconnect from groups!**")

    else:
        await message.reply(f"""

Hey there {message.from_user.mention}, 

I am {BOT_NAME},special Group manager Bot to help
you to protect and manage your Groups
I am a Powerful Assistant[🧛](https://telegra.ph/file/2fcbedac71233eeaa3ac9.jpg)""",reply_markup=home_keyboard_pm)

        return await add_served_user(chat_id) 


@app.on_message(filters.command(HELP_COMMAND))
@language
async def help_command(client, message: Message, _):

    if message.chat.type != "private":

        if len(message.command) >= 2:

            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()

            if str(name) in HELPABLE:

                key = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text=_["main3"], url=f"t.me/{BOT_USERNAME}?start=help_{name}")]])

                await message.reply(_["main4"],reply_markup=key)

            else:
                await message.reply(_["main2"], reply_markup=keyboard)

        else:
            await message.reply(_["main2"], reply_markup=keyboard)

    else:
        if len(message.command) >= 2:

            name = (message.text.split(None, 1)[1]).replace(" ", "_").lower()

            if str(name) in HELPABLE:

                text = (_["main6"].format({HELPABLE[name].__MODULE__}
                + HELPABLE[name].__HELP__))

                if hasattr(HELPABLE[name], "__helpbtns__"):

                       button = (HELPABLE[name].__helpbtns__) + [[InlineKeyboardButton("Back", callback_data="bot_commands")]]

                if not hasattr(HELPABLE[name], "__helpbtns__"): button = [[InlineKeyboardButton("Back", callback_data="bot_commands")]]

                await message.reply(text,reply_markup=InlineKeyboardMarkup(button),disable_web_page_preview=True)

            else:
                text, help_keyboard = await help_parser(message.from_user.first_name)

                await message.reply(_["main5"],reply_markup=help_keyboard,disable_web_page_preview=True)

        else:
            text, help_keyboard = await help_parser(message.from_user.first_name)

            await message.reply(
                text, reply_markup=help_keyboard, disable_web_page_preview=True
            )

    return
  
@app.on_callback_query(filters.regex("startcq"))
@languageCB
async def startcq(client,CallbackQuery, _):
    await CallbackQuery.message.edit(text=f"""
Hey there {CallbackQuery.from_user.mention}, 

I am {BOT_NAME},special Group manager Bot to help
you to protect and manage your Groups
I am a Powerful Assistant[🧛](https://telegra.ph/file/2fcbedac71233eeaa3ac9.jpg)""",disable_web_page_preview=True,reply_markup=home_keyboard_pm)


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
"""
**Welcome to help menu**

An anime - Themed advanced telegram Group management
Bot For help You to Manage & Protect Your Groups.
[🥷🏻](https://telegra.ph/file/ff6aed6e8d83b46fea6e0.jpg)""",keyboard)


@app.on_callback_query(filters.regex("bot_commands"))
@languageCB
async def commands_callbacc(client,CallbackQuery, _):

    text ,keyboard = await help_parser(CallbackQuery.from_user.mention)

    await CallbackQuery.message.edit(text=_["main5"],reply_markup=keyboard,disable_web_page_preview=True)


@app.on_callback_query(filters.regex(r"help_(.*?)"))
@languageCB
async def help_button(client, query, _):

    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    create_match = re.match(r"help_create", query.data)

    top_text = _["main5"]

    if mod_match:
        module = (mod_match.group(1)).replace(" ", "_")
        text = (
            "{} **{}**:\n".format(
                "Here is the help for", HELPABLE[module].__MODULE__
            )
            + HELPABLE[module].__HELP__)

        if hasattr(HELPABLE[module], "__helpbtns__"):
                       button = (HELPABLE[module].__helpbtns__) + [[InlineKeyboardButton("Back", callback_data="bot_commands")]]

        if not hasattr(HELPABLE[module], "__helpbtns__"): button = [[InlineKeyboardButton("Back", callback_data="bot_commands")]]

        await query.message.edit(text=text,reply_markup=InlineKeyboardMarkup(button),disable_web_page_preview=True,)

    elif home_match:
        await query.message.edit(query.from_user.id,text= _["main2"],reply_markup=home_keyboard_pm)

    elif prev_match:
        curr_page = int(prev_match.group(1))

        await query.message.edit(text=top_text,reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page - 1, HELPABLE, "help")),disable_web_page_preview=True)

    elif next_match:
        next_page = int(next_match.group(1))

        await query.message.edit(text=top_text,reply_markup=InlineKeyboardMarkup(paginate_modules(next_page + 1, HELPABLE, "help")),disable_web_page_preview=True)

    elif back_match:
        await query.message.edit(text=top_text,reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),disable_web_page_preview=True)

    elif create_match:
        text, keyboard = await help_parser(query)

        await query.message.edit(text=text,reply_markup=keyboard,disable_web_page_preview=True)

    return await client.answer_callback_query(query.id)

from pymongo import MongoClient

client = MongoClient(MONGO_URL)

users = client['moin']['bots']


def already_db(user_id):
        user = users.find_one({"bot_token" : str(user_id)})
        if not user:
            return False
        return True

def add_user(user_id):
    in_db = already_db(user_id)
    if in_db:
        return
    return users.insert_one({"bot_token": str(user_id)}) 

def remove_user(user_id):
    in_db = already_db(user_id)
    if not in_db:
        return 
    return users.delete_one({"bot_token": str(user_id)})

@app.on_message(filters.private & filters.command("clone"))
async def clone(_,message):
    text = await message.reply("Usage:\n\n /clone token")
    TOKEN = message.command[1]

    add_user(TOKEN)
  
    try:
        m = await text.edit("Booting Your Client")
        client = Client( ":memory:", API_ID, API_HASH, bot_token=TOKEN, in_memory=True, plugins={"root": "handlers"})
        await client.start()
        idle()
        user = await client.get_me()
        await m.edit(f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning.")
    
    except Exception as e:
        await message.reply(f"**ERROR:** `{str(e)}`\nPress /start to Start again.")


op = users.find()

for kk in op:
    nam = [kk['bot_token']]

    for usr in nam:
        try:
            print(usr)
            app = Client("cache",api_id=API_ID, api_hash=API_HASH, bot_token=usr ,in_memory=True, plugins={"root": "handlers"})
            app.start()

        except errors.bad_request_400.AccessTokenExpired as e:
            remove_user(usr)


if __name__ == "__main__":

    install()

    with closing(loop):

        with suppress(asyncio.exceptions.CancelledError):
            loop.run_until_complete(start_bot())

        loop.run_until_complete(asyncio.sleep(1.0)) 
