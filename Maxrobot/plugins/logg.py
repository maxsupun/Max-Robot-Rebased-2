import re
from Maxrobot import app as sz
from io import BytesIO
from requests import get
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os 
from PIL import Image


repmark = InlineKeyboardMarkup(
      [
        [
        InlineKeyboardButton(text="➕ Add me to your group ➕", url=f"http://t.me/The_Max_Robot?startgroup=botstart") 
        ],
        [
         InlineKeyboardButton(text="🗣Join my updates ", url=f"https://t.me/MaxRobot_updates") 
        ]
      ]      
    )

def nospace(s):

    s = re.sub(r"\s+", '%20', s)

    return s
@sz.on_message(filters.command(["logo", f"logo@Max123Robot"]))
async def make_logo(_, message):
    imgcaption = f"""
☘️ Logo Created Successfully✅
◇───────────────◇
🔥 Created by :@The_Max_Robot
🌷 Requestor : {message.from_user.mention}
@MaxRobot_updates⚡
◇───────────────◇
©2021 All Right Reserved⚠️
"""
    if len(message.command) < 2:
            return await message.reply_text("Please give a text to make logo")
    m = await message.reply_text("📸 Creating..")
    name = message.text.split(None, 1)[1] if len(message.command) < 3 else message.text.split(None, 1)[1].replace(" ", "%20")
    api = get(f"https://api.singledevelopers.software/logo?name={name}")
    await m.edit("📤 Uploading ...")
    await sz.send_chat_action(message.chat.id, "upload_photo")
    img = Image.open(BytesIO(api.content))
    logoname = "maxlogo.png"
    img.save(logoname, "png")
    await message.reply_photo(photo = logoname,
                              caption=imgcaption,
                              reply_markup = repmark)
    await m.delete()
    if os.path.exists(logoname):
            os.remove(logoname)

__MODULE__ = "Logo Maker"
__HELP__ = """
** logo Maker **
❍ /logo <name>: Get creative logos.
"""
