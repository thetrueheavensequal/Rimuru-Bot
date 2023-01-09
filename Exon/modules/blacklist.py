import html
import re

from telegram import ChatPermissions, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import mention_html

import Exon.modules.sql.blacklist_sql as sql
from Exon import LOGGER, application
from Exon.modules.connection import connected
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.alternate import send_message, typing_action
from Exon.modules.helper_funcs.chat_status import check_admin, user_not_admin
from Exon.modules.helper_funcs.extraction import extract_text
from Exon.modules.helper_funcs.misc import split_message
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable
from Exon.modules.sql.approve_sql import is_approved
from Exon.modules.warns import warn

BLACKLIST_GROUP = 11


@check_admin(is_user=True)
@typing_action
async def blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    conn = await connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    filter_list = "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs ɪɴ <b>{}</b>:\n".format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    # for trigger in all_blacklisted:
    #     filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs ɪɴ <b>{}</b>:\n".format(
            html.escape(chat_name),
        ):
            await send_message(
                update.effective_message,
                "ɴᴏ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs ɪɴ <b>{}</b>!".format(html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )
            return
        await send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@check_admin(is_user=True)
@typing_action
async def add_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = await connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )
        for trigger in to_blacklist:
            sql.add_to_blacklist(chat_id, trigger.lower())

        if len(to_blacklist) == 1:
            await send_message(
                update.effective_message,
                "ᴀᴅᴅᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ <code>{}</code> ɪɴ ᴄʜᴀᴛ: <b>{}</b>!".format(
                    html.escape(to_blacklist[0]),
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            await send_message(
                update.effective_message,
                "ᴀᴅᴅᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ ᴛʀɪɢɢᴇʀ: <code>{}</code> in <b>{}</b>!".format(
                    len(to_blacklist),
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )

    else:
        await send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜɪᴄʜ ᴡᴏʀᴅs ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴀᴅᴅ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ.",
        )


@check_admin(is_user=True)
@typing_action
async def unblacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = await connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )
        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                await send_message(
                    update.effective_message,
                    "ʀᴇᴍᴏᴠᴇᴅ <code>{}</code> ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{}</b>!".format(
                        html.escape(to_unblacklist[0]),
                        html.escape(chat_name),
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                await send_message(
                    update.effective_message,
                    "ᴛʜɪs ɪs ɴᴏᴛ ᴀ ʙʟᴀᴄᴋʟɪsᴛ ᴛʀɪɢɢᴇʀ!",
                )

        elif successful == len(to_unblacklist):
            await send_message(
                update.effective_message,
                "ʀᴇᴍᴏᴠᴇᴅ <code>{}</code> ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{}</b>!".format(
                    successful,
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            await send_message(
                update.effective_message,
                "ɴᴏɴᴇ ᴏғ ᴛʜᴇsᴇ ᴛʀɪɢɢᴇʀs ᴇxɪsᴛ sᴏ ɪᴛ ᴄᴀɴ'ᴛ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ.",
                parse_mode=ParseMode.HTML,
            )

        else:
            await send_message(
                update.effective_message,
                "Removed <code>{}</code> from blacklist. {} did not exist, "
                "sᴏ ᴡᴇʀᴇ ɴᴏᴛ ʀᴇᴍᴏᴠᴇᴅ.".format(
                    successful,
                    len(to_unblacklist) - successful,
                ),
                parse_mode=ParseMode.HTML,
            )
    else:
        await send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜɪᴄʜ ᴡᴏʀᴅs ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ !",
        )


@loggable
@check_admin(is_user=True)
@typing_action
async def blacklist_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = context.args

    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = await application.bot.getChat(conn)
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == "private":
            await send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴏɴʟʏ ᴜsᴇᴅ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ ᴘᴍ",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "ᴅᴏ ɴᴏᴛʜɪɴɢ"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "ᴅᴇʟᴇᴛᴇ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴍᴇssᴀɢᴇ"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "ᴡᴀʀɴ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "ᴍᴜᴛᴇ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "ᴋɪᴄᴋ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ʙᴀɴ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ғᴏʀ ʙʟᴀᴄᴋʟɪsᴛ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/blacklistmode tban <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.

ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ value: 4m = 4 ᴍɪɴᴜᴛᴇs, 3h = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                await send_message(
                    update.effective_message, teks, parse_mode="markdown"
                )
                return ""
            restime = await extract_time(msg, args[1])
            if not restime:
                teks = """ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ!
ᴇxᴀᴍᴘʟᴇ ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4ᴍ = 4 ᴍɪɴᴜᴛᴇs, 3h = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                await send_message(
                    update.effective_message, teks, parse_mode="markdown"
                )
                return ""
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴ ғᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """It ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ғᴏʀ ʙʟᴀᴄᴋʟɪsᴛ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ  ᴛɪᴍᴇ; ᴛʀʏ, `/blacklistmode tmute <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.

ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4m = 4 ᴍɪɴᴜᴛᴇs, 3h = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                await send_message(
                    update.effective_message, teks, parse_mode="markdown"
                )
                return ""
            restime = await extract_time(msg, args[1])
            if not restime:
                teks = """ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ!
ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4m = 4 ᴍɪɴᴜᴛᴇs, 3h = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                await send_message(
                    update.effective_message, teks, parse_mode="markdown"
                )
                return ""
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇ ғᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            await send_message(
                update.effective_message,
                "I ᴏɴʟʏ ᴜɴᴅᴇʀsᴛᴀɴᴅ: ᴏғғ/ᴅᴇʟ/ᴡᴀʀɴ/ʙᴀɴ/ᴋɪᴄᴋ/ᴍᴜᴛᴇ/ᴛʙᴀɴ/ᴛᴍᴜᴛᴇ!",
            )
            return ""
        if conn:
            text = "ᴄʜᴀɴɢᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴏᴅᴇ: `{}` in *{}*!".format(
                settypeblacklist,
                chat_name,
            )
        else:
            text = "ᴄʜᴀɴɢᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ mode: `{}`!".format(settypeblacklist)
        await send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>ᴀᴅᴍɪɴ:</b> {}\n"
            "ᴄʜᴀɴɢᴇᴅ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴏᴅᴇ. ᴡɪʟʟ {}.".format(
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
                settypeblacklist,
            )
        )
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "ᴅᴏ ɴᴏᴛʜɪɴɢ"
        elif getmode == 1:
            settypeblacklist = "ᴅᴇʟᴇᴛᴇ"
        elif getmode == 2:
            settypeblacklist = "ᴡᴀʀɴ"
        elif getmode == 3:
            settypeblacklist = "ᴍᴜᴛᴇ"
        elif getmode == 4:
            settypeblacklist = "ᴋɪᴄᴋ"
        elif getmode == 5:
            settypeblacklist = "ʙᴀɴ"
        elif getmode == 6:
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴ ғᴏʀ {}".format(getvalue)
        elif getmode == 7:
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇ for {}".format(getvalue)
        if conn:
            text = "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴍᴏᴅᴇ: *{}* ɪɴ *{}*.".format(
                settypeblacklist,
                chat_name,
            )
        else:
            text = "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴍᴏᴅᴇ: *{}*.".format(settypeblacklist)
        await send_message(
            update.effective_message, text, parse_mode=ParseMode.MARKDOWN
        )
    return ""


def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


@user_not_admin
async def del_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    bot = context.bot
    to_match = await extract_text(message)
    if not to_match:
        return
    if is_approved(chat.id, user.id):
        return
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    try:
                        await message.delete()
                    except BadRequest:
                        pass
                elif getmode == 2:
                    try:
                        await message.delete()
                    except BadRequest:
                        pass
                    warn(
                        update.effective_user,
                        chat,
                        ("ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴛʀɪɢɢᴇʀ: {}".format(trigger)),
                        message,
                        update.effective_user,
                    )
                    return
                elif getmode == 3:
                    await message.delete()
                    await bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    await bot.sendMessage(
                        chat.id,
                        f"ᴍᴜᴛᴇᴅ {user.first_name} ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
                elif getmode == 4:
                    await message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        await bot.sendMessage(
                            chat.id,
                            f"ᴋɪᴄᴋᴇᴅ {user.first_name} ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                            message_thread_id=message.message_thread_id
                            if chat.is_forum
                            else None,
                        )
                    return
                elif getmode == 5:
                    await message.delete()
                    await chat.ban_member(user.id)
                    await bot.sendMessage(
                        chat.id,
                        f"ʙᴀɴɴᴇᴅ {user.first_name} ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
                elif getmode == 6:
                    await message.delete()
                    bantime = await extract_time(message, value)
                    await chat.ban_member(user.id, until_date=bantime)
                    await bot.sendMessage(
                        chat.id,
                        f"ʙᴀɴɴᴇᴅ {user.first_name} ᴜɴᴛɪʟ '{value}' ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ word: {trigger}!",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
                elif getmode == 7:
                    await message.delete()
                    mutetime = await extract_time(message, value)
                    await bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        until_date=mutetime,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    await bot.sendMessage(
                        chat.id,
                        f"ᴍᴜᴛᴇᴅ {user.first_name} ᴜɴᴛɪʟ '{value}' ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
            except BadRequest as excp:
                if excp.message != "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                    LOGGER.exception("ᴇʀʀᴏʀ ᴡʜɪʟᴇ ᴅᴇʟᴇᴛɪɴɢ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴇssᴀɢᴇ.")
            break


async def __import_data__(chat_id, data, message):
    # set chat blacklist
    blacklist = data.get("blacklist", {})
    for trigger in blacklist:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_blacklist_chat_filters(chat_id)
    return "ᴛʜᴇʀᴇ ᴀʀᴇ {} ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs.".format(blacklisted)


def __stats__():
    return "• {} ʙʟᴀᴄᴋʟɪsᴛ ᴛʀɪɢɢᴇʀs, ᴀᴄʀᴏss {} ᴄʜᴀᴛs.".format(
        sql.num_blacklist_filters(),
        sql.num_blacklist_filter_chats(),
    )


__mod_name__ = "ʙʟᴀᴄᴋʟɪsᴛ"

__help__ = """

ʙʟᴀᴄᴋʟɪsᴛs ᴀʀᴇ ᴜsᴇᴅ ᴛᴏ sᴛᴏᴘ ᴄᴇʀᴛᴀɪɴ ᴛʀɪɢɢᴇʀs ғʀᴏᴍ ʙᴇɪɴɢ sᴀɪᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ. ᴀɴʏ ᴛɪᴍᴇ ᴛʜᴇ ᴛʀɪɢɢᴇʀ ɪs ᴍᴇɴᴛɪᴏɴᴇᴅ, ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ. ᴀ ɢᴏᴏᴅ ᴄᴏᴍʙᴏ ɪs sᴏᴍᴇᴛɪᴍᴇs ᴛᴏ ᴘᴀɪʀ ᴛʜɪs ᴜᴘ ᴡɪᴛʜ ᴡᴀʀɴ ғɪʟᴛᴇʀs!

*NOTE*: ʙʟᴀᴄᴋʟɪsᴛs ᴅᴏ ɴᴏᴛ ᴀғғᴇᴄᴛ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs :

 • /blacklist*:* ᴠɪᴇᴡ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs.

*ᴀᴅᴍɪɴ ᴏɴʟʏ:*
 • /addblacklist <ᴛʀɪɢɢᴇʀs>*:* ᴀᴅᴅ ᴀ ᴛʀɪɢɢᴇʀ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ. ᴇᴀᴄʜ ʟɪɴᴇ ɪs ᴄᴏɴsɪᴅᴇʀᴇᴅ ᴏɴᴇ ᴛʀɪɢɢᴇʀ, sᴏ ᴜsɪɴɢ ᴅɪғғᴇʀᴇɴᴛ ʟɪɴᴇs ᴡɪʟʟ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴀᴅᴅ ᴍᴜʟᴛɪᴘʟᴇ ᴛʀɪɢɢᴇʀs.
 • /unblacklist <triggers>*:* ʀᴇᴍᴏᴠᴇ ᴛʀɪɢɢᴇʀs ғʀᴏᴍ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ. sᴀᴍᴇ ɴᴇᴡʟɪɴᴇ ʟᴏɢɪᴄ ᴀᴘᴘʟɪᴇs ʜᴇʀᴇ, sᴏ ʏᴏᴜ can ʀᴇᴍᴏᴠᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴛʀɪɢɢᴇʀs ᴀᴛ ᴏɴᴄᴇ.
 • /blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>*:* ᴀᴄᴛɪᴏɴ ᴛᴏ ᴘᴇʀғᴏʀᴍ when sᴏᴍᴇᴏɴᴇ sᴇɴᴅs ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs.
"""
BLACKLIST_HANDLER = DisableAbleCommandHandler(
    "blacklist", blacklist, admin_ok=True, block=False
)
ADD_BLACKLIST_HANDLER = CommandHandler("addblacklist", add_blacklist, block=False)
UNBLACKLIST_HANDLER = CommandHandler("unblacklist", unblacklist, block=False)
BLACKLISTMODE_HANDLER = CommandHandler("blacklistmode", blacklist_mode, block=False)
BLACKLIST_DEL_HANDLER = MessageHandler(
    (filters.TEXT | filters.COMMAND | filters.Sticker.ALL | filters.PHOTO)
    & filters.ChatType.GROUPS,
    del_blacklist,
    allow_edit=True,
    block=False,
)

application.add_handler(BLACKLIST_HANDLER)
application.add_handler(ADD_BLACKLIST_HANDLER)
application.add_handler(UNBLACKLIST_HANDLER)
application.add_handler(BLACKLISTMODE_HANDLER)
application.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)

__handlers__ = [
    BLACKLIST_HANDLER,
    ADD_BLACKLIST_HANDLER,
    UNBLACKLIST_HANDLER,
    BLACKLISTMODE_HANDLER,
    (BLACKLIST_DEL_HANDLER, BLACKLIST_GROUP),
]
