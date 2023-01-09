import json
import os
import time
from io import BytesIO

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes

# from Exon.modules.sql import warns_sql as warnssql
import Exon.modules.sql.blacklist_sql as blacklistsql

# from Exon.modules.sql import cust_filters_sql as filtersql
# import Exon.modules.sql.welcome_sql as welcsql
import Exon.modules.sql.locks_sql as locksql
import Exon.modules.sql.notes_sql as sql

# from Exon.modules.rules import get_rules
import Exon.modules.sql.rules_sql as rulessql
from Exon import EVENT_LOGS, LOGGER, OWNER_ID, SUPPORT_CHAT, application
from Exon.__main__ import DATA_IMPORT
from Exon.modules.connection import connected
from Exon.modules.helper_funcs.alternate import typing_action
from Exon.modules.helper_funcs.chat_status import check_admin
from Exon.modules.sql import disable_sql as disabledsql


@typing_action
@check_admin(is_user=True)
async def import_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    # TODO: allow uploading doc with command, not just as reply
    # only work with a doc

    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = await application.bot.getChat(conn)
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == "private":
            await update.effective_message.reply_text("ᴛʜɪs ɪs ᴀ ɢʀᴏᴜᴘ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!")
            return ""

        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    if msg.reply_to_message and msg.reply_to_message.document:
        try:
            file_info = await context.bot.get_file(
                msg.reply_to_message.document.file_id
            )
        except BadRequest:
            await msg.reply_text(
                "ᴛʀʏ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴀɴᴅ ᴜᴘʟᴏᴀᴅɪɴɢ ᴛʜᴇ ғɪʟᴇ ʏᴏᴜʀsᴇʟғ ᴀɢᴀɪɴ, ᴛʜɪs ᴏɴᴇ sᴇᴇᴍ ʙʀᴏᴋᴇɴ ᴛᴏ ᴍᴇ!",
            )
            return

        with BytesIO() as file:
            await file_info.download_to_memory(out=file)
            file.seek(0)
            data = json.load(file)

        # only import one group
        if len(data) > 1 and str(chat.id) not in data:
            await msg.reply_text(
                "ᴛʜᴇʀᴇ ᴀʀᴇ ᴍᴏʀᴇ ᴛʜᴀɴ ᴏɴᴇ ɢʀᴏᴜᴘ ɪɴ ᴛʜɪs ғɪʟᴇ ᴀɴᴅ ᴛʜᴇ ᴄʜᴀᴛ.ɪᴅ ɪs ɴᴏᴛ sᴀᴍᴇ! ʜᴏᴡ ᴀᴍ i sᴜᴘᴘᴏsᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ ɪᴛ?",
            )
            return

        # Check if backup is this chat
        try:
            if data.get(str(chat.id)) is None:
                if conn:
                    text = "ʙᴀᴄᴋᴜᴘ ᴄᴏᴍᴇs ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ chat, ɪ ᴄᴀɴ'ᴛ ʀᴇᴛᴜʀɴ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀᴛ ᴛᴏ ᴄʜᴀᴛ *{}*".format(
                        chat_name,
                    )
                else:
                    text = "ʙᴀᴄᴋᴜᴘ ᴄᴏᴍᴇs ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀᴛ, I ᴄᴀɴ'ᴛ ʀᴇᴛᴜʀɴ ᴀɴᴏᴛʜᴇʀ ᴄʜᴀᴛ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ"
                return msg.reply_text(text, parse_mode="markdown")
        except Exception:
            return msg.reply_text("ᴛʜᴇʀᴇ ᴡᴀs ᴀ ᴘʀᴏʙʟᴇᴍ ᴡʜɪʟᴇ ɪᴍᴘᴏʀᴛɪɴɢ ᴛʜᴇ ᴅᴀᴛᴀ!")
        # Check if backup is from self
        try:
            if str(context.bot.id) != str(data[str(chat.id)]["bot"]):
                return msg.reply_text(
                    "ʙᴀᴄᴋᴜᴘ ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ ᴛʜᴀᴛ ɪs ɴᴏᴛ sᴜɢɢᴇsᴛᴇᴅ ᴍɪɢʜᴛ ᴄᴀᴜsᴇ ᴛʜᴇ ᴘʀᴏʙʟᴇᴍ, ᴅᴏᴄᴜᴍᴇɴᴛs, ᴘʜᴏᴛᴏs, ᴠɪᴅᴇᴏs, ᴀᴜᴅɪᴏs, ʀᴇᴄᴏʀᴅs ᴍɪɢʜᴛ ɴᴏᴛ ᴡᴏʀᴋ ᴀs ɪᴛ sʜᴏᴜʟᴅ ʙᴇ.",
                )
        except Exception:
            pass
        # Select data source
        if str(chat.id) in data:
            data = data[str(chat.id)]["hashes"]
        else:
            data = data[list(data.keys())[0]]["hashes"]

        try:
            for mod in DATA_IMPORT:
                try:
                    await mod.__import_data__(str(chat.id), data, msg)
                except TypeError:
                    pass
        except Exception:
            await msg.reply_text(
                f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ʀᴇᴄᴏᴠᴇʀɪɴɢ ʏᴏᴜʀ ᴅᴀᴛᴀ. ᴛʜᴇ ᴘʀᴏᴄᴇss ғᴀɪʟᴇᴅ. ɪғ ʏᴏᴜ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴀ ᴘʀᴏʙʟᴇᴍ ᴡɪᴛʜ ᴛʜɪs, ᴘʟᴇᴀsᴇ ᴛᴀᴋᴇ ɪᴛ ᴛᴏ @{SUPPORT_CHAT}",
            )

            LOGGER.exception(
                "ɪᴍᴘᴏʀᴛ ғᴏʀ ᴛʜᴇ ᴄʜᴀᴛ %s ᴡɪᴛʜ ᴛʜᴇ ɴᴀᴍᴇ %s ғᴀɪʟᴇᴅ.",
                str(chat.id),
                str(chat.title),
            )
            return

        # TODO: some of that link logic
        # NOTE: consider default permissions stuff?
        if conn:

            text = "ʙᴀᴄᴋᴜᴘ ғᴜʟʟʏ ʀᴇsᴛᴏʀᴇᴅ ᴏɴ *{}*.".format(chat_name)
        else:
            text = "ʙᴀᴄᴋᴜᴘ ғᴜʟʟʏ ʀᴇsᴛᴏʀᴇᴅ"
        await msg.reply_text(text, parse_mode="markdown")
    else:
        await msg.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ ᴇxᴘᴏʀᴛᴇᴅ ʙᴀᴄᴋᴜᴘ ᴅᴏᴄᴜᴍᴇɴᴛ.")
        return


@check_admin(is_user=True)
async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_data = context.chat_data
    msg = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat_id = update.effective_chat.id
    chat = update.effective_chat
    current_chat_id = update.effective_chat.id
    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = await application.bot.getChat(conn)
        chat_id = conn
        # chat_name = await application.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            await update.effective_message.reply_text("ᴛʜɪs ɪs ᴀ ɢʀᴏᴜᴘ ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅ!")
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        # chat_name = update.effective_message.chat.title

    jam = time.time()
    new_jam = jam + 10800
    checkchat = get_chat(chat_id, chat_data)
    if checkchat.get("status"):
        if jam <= int(checkchat.get("value")):
            timeformatt = time.strftime(
                "%H:%M:%S %d/%m/%Y",
                time.localtime(checkchat.get("value")),
            )
            await update.effective_message.reply_text(
                "ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ʙᴀᴄᴋᴜᴘ ᴏɴᴄᴇ ᴀ ᴅᴀʏ!\nʏᴏᴜ ᴄᴀɴ ʙᴀᴄᴋᴜᴘ ᴀɢᴀɪɴ ɪɴ ᴀʙᴏᴜᴛ `{}`".format(
                    timeformatt,
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        else:
            if user.id != OWNER_ID:
                put_chat(chat_id, new_jam, chat_data)
    else:
        if user.id != OWNER_ID:
            put_chat(chat_id, new_jam, chat_data)

    note_list = sql.get_all_chat_notes(chat_id)
    backup = {}
    # button = ""
    buttonlist = []
    namacat = ""
    isicat = ""
    rules = ""
    count = 0
    countbtn = 0
    # Notes
    for note in note_list:
        count += 1
        # getnote = sql.get_note(chat_id, note.name)
        namacat += "{}<###splitter###>".format(note.name)
        if note.msgtype == 1:
            tombol = sql.get_buttons(chat_id, note.name)
            # keyb = []
            for btn in tombol:
                countbtn += 1
                if btn.same_line:
                    buttonlist.append(
                        ("{}".format(btn.name), "{}".format(btn.url), True),
                    )
                else:
                    buttonlist.append(
                        ("{}".format(btn.name), "{}".format(btn.url), False),
                    )
            isicat += "###button###: {}<###button###>{}<###splitter###>".format(
                note.value,
                str(buttonlist),
            )
            buttonlist.clear()
        elif note.msgtype == 2:
            isicat += "###sticker###:{}<###splitter###>".format(note.file)
        elif note.msgtype == 3:
            isicat += "###file###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file,
                note.value,
            )
        elif note.msgtype == 4:
            isicat += "###photo###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file,
                note.value,
            )
        elif note.msgtype == 5:
            isicat += "###audio###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file,
                note.value,
            )
        elif note.msgtype == 6:
            isicat += "###voice###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file,
                note.value,
            )
        elif note.msgtype == 7:
            isicat += "###video###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file,
                note.value,
            )
        elif note.msgtype == 8:
            isicat += "###video_note###:{}<###TYPESPLIT###>{}<###splitter###>".format(
                note.file,
                note.value,
            )
        else:
            isicat += "{}<###splitter###>".format(note.value)
    notes = {
        "#{}".format(namacat.split("<###splitter###>")[x]): "{}".format(
            isicat.split("<###splitter###>")[x],
        )
        for x in range(count)
    }
    # Rules
    rules = rulessql.get_rules(chat_id)
    # Blacklist
    bl = list(blacklistsql.get_chat_blacklist(chat_id))
    # Disabled command
    disabledcmd = list(disabledsql.get_all_disabled(chat_id))
    # Filters (TODO)
    """
	all_filters = list(filtersql.get_chat_triggers(chat_id))
	export_filters = {}
	for filters in all_filters:
		filt = filtersql.get_filter(chat_id, filters)
		# print(vars(filt))
		if filt.is_sticker:
			tipefilt = "sticker"
		elif filt.is_document:
			tipefilt = "doc"
		elif filt.is_image:
			tipefilt = "img"
		elif filt.is_audio:
			tipefilt = "audio"
		elif filt.is_voice:
			tipefilt = "voice"
		elif filt.is_video:
			tipefilt = "video"
		elif filt.has_buttons:
			tipefilt = "button"
			buttons = filtersql.get_buttons(chat.id, filt.keyword)
			print(vars(buttons))
		elif filt.has_markdown:
			tipefilt = "text"
		if tipefilt == "button":
			content = "{}#=#{}|btn|{}".format(tipefilt, filt.reply, buttons)
		else:
			content = "{}#=#{}".format(tipefilt, filt.reply)
		print(content)
		export_filters[filters] = content
	print(export_filters)
	"""
    # Welcome (TODO)
    # welc = welcsql.get_welc_pref(chat_id)
    # Locked
    curr_locks = locksql.get_locks(chat_id)
    curr_restr = locksql.get_restr(chat_id)

    if curr_locks:
        locked_lock = {
            "sticker": curr_locks.sticker,
            "audio": curr_locks.audio,
            "voice": curr_locks.voice,
            "document": curr_locks.document,
            "video": curr_locks.video,
            "contact": curr_locks.contact,
            "photo": curr_locks.photo,
            "gif": curr_locks.gif,
            "url": curr_locks.url,
            "bots": curr_locks.bots,
            "forward": curr_locks.forward,
            "game": curr_locks.game,
            "location": curr_locks.location,
            "rtl": curr_locks.rtl,
        }
    else:
        locked_lock = {}

    if curr_restr:
        locked_restr = {
            "messages": curr_restr.messages,
            "media": curr_restr.media,
            "other": curr_restr.other,
            "previews": curr_restr.preview,
            "all": all(
                [
                    curr_restr.messages,
                    curr_restr.media,
                    curr_restr.other,
                    curr_restr.preview,
                ],
            ),
        }
    else:
        locked_restr = {}

    locks = {"locks": locked_lock, "restrict": locked_restr}
    # Warns (TODO)
    # warns = warnssql.get_warns(chat_id)
    # Backing up
    backup[chat_id] = {
        "bot": context.bot.id,
        "hashes": {
            "info": {"rules": rules},
            "extra": notes,
            "blacklist": bl,
            "disabled": disabledcmd,
            "locks": locks,
        },
    }
    baccinfo = json.dumps(backup, indent=4)
    with open("Exon{}.backup".format(chat_id), "w") as f:
        f.write(str(baccinfo))
    await context.bot.sendChatAction(current_chat_id, "upload_document")
    tgl = time.strftime("%H:%M:%S - %d/%m/%Y", time.localtime(time.time()))
    try:
        await context.bot.sendMessage(
            EVENT_LOGS,
            "*sᴜᴄᴄᴇssғᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ʙᴀᴄᴋᴜᴘ:*\nᴄʜᴀᴛ: `{}`\nᴄʜᴀᴛ ɪᴅ: `{}`\nᴏɴ: `{}`".format(
                chat.title,
                chat_id,
                tgl,
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    except BadRequest:
        pass
    await context.bot.sendDocument(
        current_chat_id,
        document=open("Exon{}.backup".format(chat_id), "rb"),
        caption="*sᴜᴄᴄᴇssғᴜʟʟʏ ᴇxᴘᴏʀᴛᴇᴅ ʙᴀᴄᴋᴜᴘ:*\nᴄʜᴀᴛ: `{}`\nᴄʜᴀᴛ ɪᴅ: `{}`\nᴏɴ: `{}`\n\nɴᴏᴛᴇ: ᴛʜɪs `Exon-Backup` ᴡᴀs sᴘᴇᴄɪᴀʟʟʏ ᴍᴀᴅᴇ ғᴏʀ  ɴᴏᴛᴇs.".format(
            chat.title,
            chat_id,
            tgl,
        ),
        reply_to_message_id=msg.message_id,
        parse_mode=ParseMode.MARKDOWN,
        message_thread_id=msg.message_thread_id if chat.is_forum else None,
    )
    os.remove("Exon{}.backup".format(chat_id))  # Cleaning file


# Temporary data
def put_chat(chat_id, value, chat_data):
    # print(chat_data)
    status = value is not False
    chat_data[chat_id] = {"backups": {"status": status, "value": value}}


def get_chat(chat_id, chat_data):
    # print(chat_data)
    try:
        return chat_data[chat_id]["backups"]
    except KeyError:
        return {"status": False, "value": False}


__mod_name__ = "ʙᴀᴄᴋᴜᴘs"

__help__ = """
*ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ:*

 • /import: ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ʙᴀᴄᴋᴜᴘ ғɪʟᴇ ғᴏʀ ᴛʜᴇ ʙᴜᴛʟᴇʀ / ᴇᴍɪʟɪᴀ ɢʀᴏᴜᴘ ᴛᴏ ɪᴍᴘᴏʀᴛ ᴀs ᴍᴜᴄʜ ᴀs ᴘᴏssɪʙʟᴇ, ᴍᴀᴋɪɴɢ ᴛʀᴀɴsғᴇʀs ᴠᴇʀʏ ᴇᴀsʏ! \
 ɴᴏᴛᴇ ᴛʜᴀᴛ ғɪʟᴇs / ᴘʜᴏᴛᴏs ᴄᴀɴɴᴏᴛ ʙᴇ ɪᴍᴘᴏʀᴛᴇᴅ ᴅᴜᴇ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ʀᴇsᴛʀɪᴄᴛɪᴏɴs.

 • /export: ᴇxᴘᴏʀᴛ ɢʀᴏᴜᴘ ᴅᴀᴛᴀ, ᴡʜɪᴄʜ ᴡɪʟʟ ʙᴇ ᴇxᴘᴏʀᴛᴇᴅ ᴀʀᴇ: ʀᴜʟᴇs, ɴᴏᴛᴇs (ᴅᴏᴄᴜᴍᴇɴᴛs, ɪᴍᴀɢᴇs, music, ᴠɪᴅᴇᴏ, ᴀᴜᴅɪᴏ, ᴠᴏɪᴄᴇ, ᴛᴇxᴛ, ᴛᴇxᴛ ʙᴜᴛᴛᴏɴs) \

"""

IMPORT_HANDLER = CommandHandler("import", import_data, block=False)
EXPORT_HANDLER = CommandHandler("export", export_data, block=False)

application.add_handler(IMPORT_HANDLER)
application.add_handler(EXPORT_HANDLER)
