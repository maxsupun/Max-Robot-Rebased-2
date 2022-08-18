from re import escape as re_escape
from time import time
from pyrogram.types import ChatPermissions, Message
from Maxrobot.utils.regex_utils import regex_searcher
from html import escape
from pyrogram import filters
from pyrogram.types import  Message
from Maxrobot import  app,LOG_GROUP_ID
from Maxrobot.mongo.blacklistdb import Blacklist
from Maxrobot.utils.custom_filters import command, owner_filter, restrict_filter
from Maxrobot.utils.kbhelpers import rkb as ikb
from lang import get_command
from Maxrobot.utils.commands import command
from Maxrobot.utils.lang import language
from Maxrobot.utils.filter_groups import black
from Maxrobot.mongo.approvedb import Approve
from Maxrobot.mongo.warnsdb import Warns, WarnSettings
from Maxrobot.utils.caching import ADMIN_CACHE, admin_cache_reload
from Maxrobot.utils.custom_filters import command, restrict_filter
from Maxrobot.utils.parser import mention_html
from button import Blacklists

BLACKLIST = get_command("BLACKLIST")
ADDBLACK = get_command("ADDBLACK")
BLACKREASON = get_command("BLACKREASON")
UNBLCK = get_command("UNBLCK")
BLMODE = get_command("BLMODE")
RMBLALL = get_command("RMBLALL")

@app.on_message(command("blacklist") & filters.group)
@language
async def view_blacklist(client, message: Message, _):
    db = Blacklist(message.chat.id)
    blacklists_chat = (f"**Current blacklisted words**\n")
    all_blacklisted = db.get_blacklists()
    if not all_blacklisted:
        return await message.reply_text(_["black2"])
    blacklists_chat += "\n".join(f"• <code>{escape(i)}</code>" for i in all_blacklisted)
    return await message.reply_text(blacklists_chat)
    
@app.on_message(command("addblacklist") & restrict_filter)
@language
async def add_blacklist(client, message: Message, _):
    db = Blacklist(message.chat.id)
    if len(message.text.split()) < 2:
        return await message.reply_text(_["black3"])
    bl_words = ((message.text.split(None, 1)[1]).lower()).split()
    all_blacklisted = db.get_blacklists()
    already_added_words, rep_text = [], ""
    for bl_word in bl_words:
        if bl_word in all_blacklisted:
            already_added_words.append(bl_word)
            continue
        db.add_blacklist(bl_word)
    if already_added_words:
        rep_text = (", ".join([f"<code>{i}</code>" for i in bl_words])+ " already added in blacklist, skipped them!")
    await message.reply_text((("Added <code>{trigger}</code> in blacklist words!")).format(trigger=", ".join(f"<code>{i}</code>" for i in bl_words)))
    await message.stop_propagation()


@app.on_message( command(BLACKREASON) & restrict_filter)
async def blacklistreason(_, message: Message):
    db = Blacklist(message.chat.id)
    if len(message.text.split()) == 1:
        curr = db.get_reason()
        await message.reply_text(f"The current reason for blacklists warn is:\n<code>{curr}</code>",)
    else:
        reason = message.text.split(None, 1)[1]
        db.set_reason(reason)
        await message.reply_text(f"Updated reason for blacklists warn is:\n<code>{reason}</code>",)
    return


@app.on_message(command(UNBLCK) & restrict_filter)
async def rm_blacklist(_, message: Message):
    db = Blacklist(message.chat.id)
    if len(message.text.split()) < 2:
        return await message.reply_text("Please check help on how to use this this command.")
    chat_bl = db.get_blacklists()
    non_found_words, rep_text = [], ""
    bl_words = ((message.text.split(None, 1)[1]).lower()).split()
    for bl_word in bl_words:
        if bl_word not in chat_bl:
            non_found_words.append(bl_word)
            continue
        db.remove_blacklist(bl_word)
    if non_found_words == bl_words:
        return await message.reply_text("Blacklists not found!")
    if non_found_words:
        rep_text = ("Could not find " + ", ".join(f"<code>{i}</code>" for i in non_found_words)) + " in blcklisted words, skipped them."
    await message.reply_text(((f"Removed {bl_words} from blacklist words!")).format( bl_words=", ".join(f"<code>{i}</code>" for i in bl_words))+ (f"\n{rep_text}" if rep_text else ""))
    await message.stop_propagation()


@app.on_message(command(BLMODE) & restrict_filter)
async def set_bl_action(_, message: Message):
    db = Blacklist(message.chat.id)
    if len(message.text.split()) == 2:
        action = message.text.split(None, 1)[1]
        valid_actions = ("ban", "kick", "mute", "warn", "none")
        if action not in valid_actions:
            return await message.reply_text(("Choose a valid blacklist action from "+ ", ".join(f"<code>{i}</code>" for i in valid_actions)))
        db.set_action(action)
        await message.reply_text("Set action for blacklist for this to <b>{action}</b>".format(action=action))
    elif len(message.text.split()) == 1:
        action = db.get_action()
        await message.reply_text(f"""|-
      The current action for blacklists in this chat is <i><b>{action}</b></i>
      All blacklist modes delete the message containing blacklist word.
      If you want to change this, you need to specify a new action instead of it.
      Possible actions are: <code>none</code>/<code>warn</code>/<code>mute</code>/<code>ban</code>""".format(action=action))
    else:
        await message.reply_text("Please check help on how to use this this command.")
    return

@app.on_message(command(RMBLALL) & owner_filter)
async def rm_allblacklist(_, message: Message):
    db = Blacklist(message.chat.id)
    all_bls = db.get_blacklists()
    if not all_bls:
        return await message.reply_text("No notes are blacklists in this chat")
    return await message.reply_text("Are you sure you want to clear all blacklists?",reply_markup=ikb([[("⚠️ Confirm", "rm_allblacklist"), ("❌ Cancel", "close_admin")]]))

@app.on_message(filters.text & filters.group, group=black)
async def bl_watcher(_, m: Message):
    if m and not m.from_user:
        return
    bl_db = Blacklist(m.chat.id)
    async def perform_action_blacklist(m: Message, action: str, trigger: str):
        if action == "kick":
            await m.chat.kick_member(m.from_user.id, int(time() + 45))
            await m.reply_text(f"Kicked {m.from_user.username} for sending a blacklisted word!")
        elif action == "ban":
            await m.chat.kick_member(m.from_user.id)
            await m.reply_text(f"Banned {m.from_user.username} for sending a blacklisted word!")
        elif action == "mute":
            await m.chat.restrict_member(m.from_user.id,ChatPermissions())
            await m.reply_text(f"Muted {m.from_user.username} for sending a blacklisted word!")
        elif action == "warn":
            warns_settings_db = WarnSettings(m.chat.id)
            warns_db = Warns(m.chat.id)
            warn_settings = warns_settings_db.get_warnings_settings()
            warn_reason = bl_db.get_reason()
            _, num = warns_db.warn_user(m.from_user.id, warn_reason)
            if num >= warn_settings["warn_limit"]:
                if warn_settings["warn_mode"] == "kick":
                    await m.chat.ban_member(m.from_user.id,until_date=int(time() + 45))
                    action = "kicked"
                elif warn_settings["warn_mode"] == "ban":
                    await m.chat.ban_member(m.from_user.id)
                    action = "banned"
                elif warn_settings["warn_mode"] == "mute":
                    await m.chat.restrict_member(m.from_user.id, ChatPermissions())
                    action = "muted"
                return await m.reply_text(
                    (f"Warnings {num}/{warn_settings['warn_limit']}\n"f"{(await mention_html(m.from_user.first_name, m.from_user.id))} has been <b>{action}!</b>"),
                )
            await m.reply_text((
                    f"{(await mention_html(m.from_user.first_name, m.from_user.id))} warned {num}/{warn_settings['warn_limit']}\n"f"Last warn was for:\n<i>{warn_reason}</i>"))
        return
    chat_blacklists = bl_db.get_blacklists()
    if not chat_blacklists:
        return
    try:
        admin_ids = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_ids = await admin_cache_reload(m, "blacklist_watcher")
    if m.from_user.id in admin_ids:
        return
    app_users = Approve(m.chat.id).list_approved()
    if m.from_user.id in {i[0] for i in app_users}:
        return
    action = bl_db.get_action()
    for trigger in chat_blacklists:
        pattern = r"( |^|[^\w])" + re_escape(trigger) + r"( |$|[^\w])"
        match = await regex_searcher(pattern, m.text.lower())
        if not match:
            continue
        if match:
            try:
                await perform_action_blacklist(m, action, trigger)
                await m.delete()
            except Exception as e:
                return await app.send_message(LOG_GROUP_ID,text= f"{e}")
            break
    return



__MODULE__ = Blacklists
__HELP__ = """
**User Commands:**
- /blacklist: Check all the blacklists in chat.

**Admin Commands:**
- /addblacklist <trigger>: Blacklists the word in the current chat.
- /rmblacklist <trigger>: Removes the word from current Blacklisted Words in Chat.
- /unblacklist : Same as above
- /blaction <mute/kick/ban/warn/none>: Sets the action to be performed by bot when a blacklist word is detected.
- /blacklistaction: Same as above
- /blacklistmode : Same as above
- /blwarning `<reason>`: Set the default blocklist reason to warn people with.
- /blreason : Same as above
- /blacklistreason : Same as above

**Owner Only:**
- /rmallblacklist: Removes all the blacklisted words from chat
**Note:**

The Default mode for Blacklist is none,
which will just delete the messages from the chat.
"""
