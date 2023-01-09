import html

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import mention_html

from Exon import LOGGER, application
from Exon.modules.helper_funcs.chat_status import check_admin, user_not_admin
from Exon.modules.log_channel import loggable
from Exon.modules.sql import request_sql as sql

REQUEST_GROUP = 12


@check_admin(is_user=True)
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if chat.type == chat.PRIVATE:
        if len(args) >= 1:
            if args[0] in ["yes", "on"]:
                sql.set_user_setting(user.id, True)
                await message.reply_text(
                    "sᴜᴄᴄᴇsғᴜʟʟʏ sᴇᴛ ʀᴇǫᴜᴇsᴛ ʜᴀɴᴅʟɪɴɢ ᴛᴏ ᴛʀᴜᴇ\nʏᴏᴜ ᴡɪʟʟ ɴᴏᴡ ʀᴇᴄᴇɪᴠᴇ ʀᴇǫᴜᴇsᴛs ғʀᴏᴍ ᴄʜᴀᴛs ʏᴏᴜ ᴀʀᴇ ᴀᴅᴍɪɴ."
                )
            elif args[0] in ["no", "off"]:
                sql.set_user_setting(user.id, False)
                await message.reply_text(
                    "sᴜᴄᴄᴇsғᴜʟʟʏ sᴇᴛ ʀᴇǫᴜᴇsᴛ ʜᴀɴᴅʟɪɴɢ ᴛᴏ ғᴀʟsᴇ\nʏᴏᴜ ᴡɪʟʟ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ʀᴇǫᴜᴇsᴛs ғʀᴏᴍ ᴄʜᴀᴛs ʏᴏᴜ ᴀʀᴇ ᴀᴅᴍɪɴ."
                )
        else:
            await message.reply_text(
                f"ᴄᴜʀʀᴇɴᴛ ʀᴇǫᴜᴇsᴛ ʜᴀɴᴅʟɪɴɢ ᴘʀᴇғᴇʀᴇɴᴄᴇ: <code>{sql.user_should_request(user.id)}</code>",
                parse_mode="html",
            )

    else:
        if len(args) >= 1:
            if args[0] in ["yes", "on"]:
                sql.set_chat_setting(chat.id, True)
                await message.reply_text(
                    f"ʀᴇǫᴜᴇsᴛ ʜᴀɴᴅʟɪɴɢ ʜᴀs sᴜᴄᴄᴇssғᴜʟʟʏ ᴛᴜʀɴᴇᴅ ᴏɴ ɪɴ {chat.title} \nɴᴏᴡ users ᴄᴀɴ ʀᴇǫᴜᴇsᴛ ʙʏ /request ᴄᴏᴍᴍᴀɴᴅ."
                )
            elif args[0] in ["no", "off"]:
                sql.set_chat_setting(chat.id, False)
                await message.reply_text(
                    f"ʀᴇǫᴜᴇsᴛ ʜᴀɴᴅʟɪɴɢ ɪs ɴᴏᴡ ᴛᴜʀɴᴇᴅ ᴏғғ ɪɴ {chat.title}"
                )
        else:
            await message.reply_text(
                f"ᴄᴜʀʀᴇɴᴛ ʀᴇǫᴜᴇsᴛ ʜᴀɴᴅʟɪɴɢ ᴘʀᴇғᴇʀᴇɴᴄᴇ: <code>{sql.chat_should_request(chat.id)}</code>",
                parse_mode="html",
            )


@loggable
@user_not_admin
async def request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    bot = context.bot

    if chat and sql.chat_should_request(chat.id):
        chat_name = chat.title or chat.username or chat.first_name
        admin_list = await chat.get_administrators()

        if not args:
            await message.reply_text("Please give something to request")
            return ""

        if chat.type == chat.SUPERGROUP:
            request = message.text
            msg = (
                f"<b>⚠️ ʀᴇǫᴜᴇsᴛ: </b>{html.escape(chat.title)}\n"
                f"<b> • ʀᴇǫᴜᴇsᴛ by:</b> {mention_html(user.id, user.first_name)} | <code>{user.id}</code>\n"
                f"<b> • ᴄᴏɴᴛᴇɴᴛ:</b> <code>{request}</code>\n"
            )
            link = f'<b> • ʀᴇǫᴜᴇsᴛᴇᴅ ᴍᴇssᴀɢᴇ:</b> <a href="https://t.me/{chat.username}/{message.message_id}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'
            should_forward = False
        else:
            link = ""
            should_forward = True
            msg = f'{mention_html(user.id, user.first_name)} ɪs ʀᴇǫᴜᴇsᴛɪɴɢ sᴏᴍᴇᴛʜɪɴɢ ɪɴ "{html.escape(chat_name)}"'

        for admin in admin_list:
            if admin.user.is_bot:
                continue

            if sql.user_should_request(admin.user.id):
                try:
                    if not chat.type == chat.SUPERGROUP:
                        await bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )

                        if should_forward:
                            await message.forward(admin.user.id)

                    if not chat.username:
                        await bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )

                        if should_forward:
                            await message.forward(admin.user.id)

                    if chat.username and chat.type == chat.SUPERGROUP:

                        await bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                        )

                        if should_forward:
                            await message.forward(admin.user.id)

                except Forbidden:
                    pass
                except BadRequest:
                    LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ ᴡʜɪʟᴇ ʀᴇǫᴜᴇsᴛɪɴɢ ᴄᴏɴᴛᴇɴᴛ!")

        await message.reply_text(
            f"{mention_html(user.id, user.first_name)} I'ᴠᴇ sᴜʙᴍɪᴛᴛᴇᴅ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴs.",
            parse_mode=ParseMode.HTML,
        )
        return msg

    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    return f"ᴛʜɪs ᴄʜᴀᴛ ɪs sᴇᴛᴜᴘ ᴛᴏ sᴇɴᴅ ᴜsᴇʀ ʀᴇᴘᴏʀᴛs ᴛᴏ ᴀᴅᴍɪɴs, ᴠɪᴀ /request ᴀɴᴅ #request: `{sql.chat_should_request(chat_id)}`"


def __user_settings__(user_id):
    if sql.user_should_request(user_id) is True:
        text = "ʏᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ʀᴇǫᴜᴇsᴛs ғʀᴏᴍ ᴄʜᴀᴛ's ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ."
    else:
        text = "ʏᴏᴜ ᴡɪʟʟ *ɴᴏᴛ* ʀᴇᴄᴇɪᴠᴇ ʀᴇǫᴜᴇsᴛs ғʀᴏᴍ ᴄʜᴀᴛ's ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ."
    return text


SETTINGS_HANDLER = CommandHandler("requests", settings, block=False)
REQUEST_HANDLER = CommandHandler(
    "request", request, filters=filters.ChatType.GROUPS, block=False
)
HASH_REQUEST_HANDLER = MessageHandler(
    filters.Regex(r"(?i)#request(s)?"), request, block=False
)


application.add_handler(SETTINGS_HANDLER)
application.add_handler(REQUEST_HANDLER, REQUEST_GROUP)
application.add_handler(HASH_REQUEST_HANDLER)

__mod_name__ = "ʀᴇǫᴜᴇsᴛ"
__help__ = """
• /request <ᴄᴏɴᴛᴇɴᴛ>*:*  ʀᴇǫᴜᴇsᴛ ᴄᴏɴᴛᴇɴᴛ ᴛᴏ ᴀᴅᴍɪɴs.

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
 • /requests <on/off>*:* ᴄʜᴀɴɢᴇ ʀᴇǫᴜᴇsᴛ sᴇᴛᴛɪɴɢ, ᴏʀ ᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs.
   • ɪғ ᴅᴏɴᴇ ɪɴ ᴘᴍ, ᴛᴏɢɢʟᴇs ʏᴏᴜʀ sᴛᴀᴛᴜs.
   • ɪғ ɪɴ ɢʀᴏᴜᴘ, ᴛᴏɢɢʟᴇs ᴛʜᴀᴛ ɢʀᴏᴜᴘ's sᴛᴀᴛᴜs.
"""

__handlers__ = [
    (REQUEST_HANDLER, REQUEST_GROUP),
    (SETTINGS_HANDLER),
]
