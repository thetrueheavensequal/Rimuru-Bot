from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes, filters
from telegram.helpers import escape_markdown

import Exon.modules.sql.rules_sql as sql
from Exon import application
from Exon.modules.helper_funcs.chat_status import check_admin
from Exon.modules.helper_funcs.string_handling import markdown_parser, markdown_to_html


async def get_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await send_rules(update, chat_id)


# Do not async - not from a handler
async def send_rules(update, chat_id, from_pm=False):
    bot = application.bot
    user = update.effective_user  # type: Optional[User]
    reply_msg = update.message.reply_to_message
    try:
        chat = await bot.get_chat(chat_id)
    except BadRequest as excp:
        if excp.message == "Chat not found" and from_pm:
            await bot.send_message(
                user.id,
                "ᴛʜᴇ ʀᴜʟᴇs sʜᴏʀᴛᴄᴜᴛ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ ʜᴀsɴ'ᴛ ʙᴇᴇɴ sᴇᴛ ᴘʀᴏᴘᴇʀʟʏ! ᴀsᴋ ᴀᴅᴍɪɴs ᴛᴏ "
                "ғɪx ᴛʜɪs.\nᴍᴀʏʙᴇ ᴛʜᴇʏ ғᴏʀɢᴏᴛ ᴛʜᴇ ʜʏᴘʜᴇɴ ɪɴ ID",
                message_thread_id=update.effective_message.message_thread_id
                if chat.is_forum
                else None,
            )
            return
        else:
            raise

    rules = sql.get_rules(chat_id)
    text = f"ᴛʜᴇ ʀᴜʟᴇs for <b>{escape_markdown(chat.title, 2)}</b> ᴀʀᴇ:\n\n{markdown_to_html(rules)}"

    if from_pm and rules:
        await bot.send_message(
            user.id,
            text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    elif from_pm:
        await bot.send_message(
            user.id,
            "ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ʜᴀᴠᴇɴ'ᴛ sᴇᴛ ᴀɴʏ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ ʏᴇᴛ. "
            "ᴛʜɪs ᴘʀᴏʙᴀʙʟʏ ᴅᴏᴇsɴ'ᴛ ᴍᴇᴀɴ ɪᴛ's ʟᴀᴡʟᴇss ᴛʜᴏᴜɢʜ...!",
        )
    elif rules and reply_msg and not reply_msg.forum_topic_created:
        await reply_msg.reply_text(
            "ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ʀᴜʟᴇs.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʀᴜʟᴇs",
                            url=f"t.me/{bot.username}?start={chat_id}",
                        ),
                    ],
                ],
            ),
        )
    elif rules:
        await update.effective_message.reply_text(
            "ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ʀᴜʟᴇs.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʀᴜʟᴇs",
                            url=f"t.me/{bot.username}?start={chat_id}",
                        ),
                    ],
                ],
            ),
        )
    else:
        await update.effective_message.reply_text(
            "The ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ʜᴀᴠᴇɴ'ᴛ sᴇᴛ ᴀɴʏ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ ʏᴇᴛ. "
            "ᴛʜɪs ᴘʀᴏʙᴀʙʟʏ ᴅᴏᴇsɴ'ᴛ ᴍᴇᴀɴ ɪᴛ's ʟᴀᴡʟᴇss ᴛʜᴏᴜɢʜ...!",
        )


@check_admin(is_user=True)
async def set_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]
    raw_text = msg.text
    args = raw_text.split(None, 1)  # use python's maxsplit to separate cmd and args
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(raw_text)  # set correct offset relative to command
        markdown_rules = markdown_parser(
            txt,
            entities=msg.parse_entities(),
            offset=offset,
        )

        sql.set_rules(chat_id, markdown_rules)
        await update.effective_message.reply_text(
            "sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ."
        )


@check_admin(is_user=True)
async def clear_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sql.set_rules(chat_id, "")
    await update.effective_message.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʟᴇᴀʀᴇᴅ ʀᴜʟᴇs!")


def __stats__():
    return f"• {sql.num_chats()} ᴄʜᴀᴛs ʜᴀᴠᴇ ʀᴜʟᴇs sᴇᴛ."


async def __import_data__(chat_id, data, message):
    # set chat rules
    rules = data.get("info", {}).get("rules", "")
    sql.set_rules(chat_id, rules)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"ᴛʜɪs ᴄʜᴀᴛ has had it's rules set: `{bool(sql.get_rules(chat_id))}`"


__help__ = """
 • /rules*:* ɢᴇᴛ ᴛʜᴇ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
 • /setrules <ʏᴏᴜʀ ʀᴜʟᴇs ʜᴇʀᴇ>*:* sᴇᴛ ᴛʜᴇ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.
 • /clearrules*:* ᴄʟᴇᴀʀ ᴛʜᴇ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.
"""

__mod_name__ = "ʀᴜʟᴇs"

GET_RULES_HANDLER = CommandHandler(
    "rules", get_rules, filters=filters.ChatType.GROUPS, block=False
)
SET_RULES_HANDLER = CommandHandler(
    "setrules", set_rules, filters=filters.ChatType.GROUPS, block=False
)
RESET_RULES_HANDLER = CommandHandler(
    "clearrules", clear_rules, filters=filters.ChatType.GROUPS, block=False
)

application.add_handler(GET_RULES_HANDLER)
application.add_handler(SET_RULES_HANDLER)
application.add_handler(RESET_RULES_HANDLER)
