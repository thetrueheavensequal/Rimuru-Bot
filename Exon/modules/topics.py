import html

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html

from Exon import application
from Exon.modules.helper_funcs.chat_status import check_admin
from Exon.modules.log_channel import loggable

"""
# from Exon.modules.sql.topics_sql import (del_action_topic,
#                                                get_action_topic,
#                                                set_action_topic)


# @loggable
# @check_admin(permission="can_manage_topics", is_both=True)
# async def set_topic_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     message = update.effective_message
#     chat = update.effective_chat
#     user = update.effective_user

#     if chat.is_forum:
#         topic_id = message.message_thread_id
#         topic_chat = get_action_topic(chat.id)
#         if topic_chat:
#             await message.reply_text("Already a topic for actions enabled in this group, you can remove it and add new one.")
#             return ""
#         else:
#             set_action_topic(chat.id, topic_id)
#             await message.reply_text("I have successfully set this topic for actions.")
#             log_message = (
#                 f"<b>{html.escape(chat.title)}:</b>\n"
#                 f"#ACTIONTOPIC\n"
#                 f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
#                 f"<b>Topic ID:</b>{message.message_thread_id}"
#             )
#             return log_message
#     else:
#         await message.reply_text("Action Topic can be only enabled in Groups with Topic support.")
#         return ""

# @loggable
# @check_admin(permission="can_manage_topics", is_both=True)
# async def del_topic_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     message = update.effective_message
#     chat = update.effective_chat
#     user = update.effective_user

#     if chat.is_forum:
#         topic_chat = get_action_topic(chat.id)
#         if topic_chat:
#             res = del_action_topic(chat.id)
#             if res:
#                 await message.reply_text(f"Successfully removed the old topic ({topic_chat}) chat for actions, You can set new one now.")
#                 log_message = (
#                     f"<b>{html.escape(chat.title)}:</b>\n"
#                     f"#ᴅᴇʟᴀᴄᴛɪᴏɴᴛᴏᴘɪᴄ\n"
#                     f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
#                     f"<b>ᴛᴏᴘɪᴄ ɪᴅ:</b>{topic_chat}"
#                 )
#                 return log_message
#             else:
#                 await message.reply_text("I don't know this it didn't work, try again.")
#                 return ""
#         else:
#             await message.reply_text("It seems like you haven't set any topic for actions, you can set one by using /setactiontopic in the topic.")
#             return ""
#     else:
#         await message.reply_text("Action Topic can be only removed in Groups with Topic support.")
#         return ""

"""


@loggable
@check_admin(permission="can_manage_topics", is_both=True)
async def create_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if chat.is_forum:
        if len(args) < 1:
            await message.reply_text("ʏᴏᴜ ᴍᴜsᴛ ɢɪᴠᴇ ᴀ ɴᴀᴍᴇ ғᴏʀ ᴛʜᴇ ᴛᴏᴘɪᴄ ᴛᴏ ᴄʀᴇᴀᴛᴇ.")
        else:
            name = " ".join(args)
            try:
                topic = await context.bot.create_forum_topic(chat.id, name)
                await message.reply_text(
                    f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʀᴇᴀᴛᴇᴅ {topic.name}\nɪᴅ: {topic.message_thread_id}"
                    if topic
                    else "sᴏᴍᴇᴛʜɪɴɢ ʜᴀᴘᴘᴇɴᴇᴅ"
                )
                await context.bot.sendMessage(
                    chat_id=chat.id,
                    text=f"ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs {topic.name} ᴄʀᴇᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ\nɪᴅ: {topic.message_thread_id}",
                    message_thread_id=topic.message_thread_id,
                )
                log_message = (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#ɴᴇᴡᴛᴏᴘɪᴄ\n"
                    f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                    f"<b>ᴛᴏᴘɪᴄ ɴᴀᴍᴇ:</b> {topic.name}\n"
                    f"<b>ᴛᴏᴘɪᴄ ɪᴅ:</b> {topic.message_thread_id}"
                )
                return log_message
            except BadRequest as e:
                await message.reply_text(f"sᴏᴍᴇᴛʜɪɴɢ ʜᴀᴘᴘᴇɴᴇᴅ.\n{e.message}")
                return ""
    else:
        await message.reply_text("ʏᴏᴜ ᴄᴀɴ ᴄʀᴇᴀᴛᴇ ᴛᴏᴘɪᴄs ɪɴ ᴛᴏᴘɪᴄs ᴇɴᴀʙʟᴇᴅ ɢʀᴏᴜᴘ ᴏɴʟʏ.")
        return ""


@loggable
@check_admin(permission="can_manage_topics", is_both=True)
async def delete_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    if chat.is_forum:
        if len(args) > 0:
            try:
                topic_chat = await context.bot.delete_forum_topic(chat.id, args[0])
                if topic_chat:
                    await message.reply_text(f"Succesfully deleted {args[0]}")
                    log_message = (
                        f"<b>{html.escape(chat.title)}:</b>\n"
                        f"#ᴅᴇʟᴛᴏᴘɪᴄ\n"
                        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                        f"<b>ᴛᴏᴘɪᴄ ɪᴅ:</b> {args[0]}"
                    )
                    return log_message
            except BadRequest as e:
                await message.reply_text(f"sᴏᴍᴇᴛʜɪɴɢ ʜᴀᴘᴘᴇɴᴇᴅ.\n{e.message}")
                raise
        else:
            await message.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ɢɪᴠᴇ ᴛᴏᴘɪᴄ ID ᴛᴏ delete.")
            return ""
    else:
        await message.reply_text("ʏᴏᴜ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ɪɴ ᴛᴏᴘɪᴄs ᴇɴᴀʙʟᴇᴅ ɢʀᴏᴜᴘs ᴏɴʟʏ.")
        return ""


@loggable
@check_admin(permission="can_manage_topics", is_both=True)
async def close_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    if chat.is_forum:
        if len(args) > 0:
            try:
                topic_chat = await context.bot.close_forum_topic(chat.id, args[0])
                if topic_chat:
                    await message.reply_text(f"sᴜᴄᴄᴇsғᴜʟʟʏ ᴄʟᴏsᴇᴅ {args[0]}")
                    log_message = (
                        f"<b>{html.escape(chat.title)}:</b>\n"
                        f"#ᴠʟᴏsᴇ_ᴛᴏᴘɪᴄ\n"
                        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                        f"<b>ᴛᴏᴘɪᴄ ɪᴅ:</b> {args[0]}"
                    )
                    return log_message
            except BadRequest as e:
                await message.reply_text(f"sᴏᴍᴇᴛʜɪɴɢ ʜᴀᴘᴘᴇɴᴇᴅ.\n{e.message}")
                raise
        else:
            await message.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ɢɪᴠᴇ ᴛᴏᴘɪᴄ ID ᴛᴏ ᴄʟᴏsᴇ.")
            return ""
    else:
        await message.reply_text("ʏᴏᴜ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ɪɴ ᴛᴏᴘɪᴄs ᴇɴᴀʙʟᴇᴅ ɢʀᴏᴜᴘs ᴏɴʟʏ.")
        return ""


@loggable
@check_admin(permission="can_manage_topics", is_both=True)
async def open_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    if chat.is_forum:
        if len(args) > 0:
            try:
                topic_chat = await context.bot.reopen_forum_topic(chat.id, args[0])
                if topic_chat:
                    await message.reply_text(f"Succesfully Opened {args[0]}")
                    log_message = (
                        f"<b>{html.escape(chat.title)}:</b>\n"
                        f"#ᴏᴘᴇɴᴛᴏᴘɪᴄ\n"
                        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                        f"<b>ᴛᴏᴘɪᴄ ɪᴅ:</b> {args[0]}"
                    )
                    return log_message
            except BadRequest as e:
                await message.reply_text(f"sᴏᴍᴇᴛʜɪɴɢ ʜᴀᴘᴘᴇɴᴇᴅ.\n{e.message}")
                raise
        else:
            await message.reply_text("ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ɢɪᴠᴇ ᴛᴏᴘɪᴄ ID ᴛᴏ ᴏᴘᴇɴ.")
            return ""
    else:
        await message.reply_text("ʏᴏᴜ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ɪɴ ᴛᴏᴘɪᴄs ᴇɴᴀʙʟᴇᴅ ɢʀᴏᴜᴘs ᴏɴʟʏ.")
        return ""


__mod_name__ = "ᴛᴏᴘɪᴄs"

__help__ = """
ᴛᴇʟᴇɢʀᴀᴍ ɪɴᴛʀᴏᴜᴅᴜᴄᴇᴅ ɴᴇᴡ ᴡᴀʏ ᴏғ ᴍᴀɴᴀɢɪɴɢ ʏᴏᴜʀ ᴄʜᴀᴛ ᴄᴀʟʟᴇᴅ ғᴏʀᴜᴍs (ᴛᴏᴘɪᴄs)

ᴀs ᴀ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ I ʜᴀᴠᴇ sᴏᴍᴇ ᴜsᴇғᴜʟ ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ
ᴄʀᴇᴀᴛᴇ, ᴅᴇʟᴇᴛᴇ, ᴄʟᴏsᴇ ᴀɴᴅ ʀᴇᴏᴘᴇɴ ᴛᴏᴘɪᴄs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ

• /topicnew*:* ᴄʀᴇᴀᴛᴇ ɴᴇᴡ ᴛᴏᴘɪᴄ, ʀᴇǫᴜɪʀᴇs ᴛᴏᴘɪᴄ ɴᴀᴍᴇ ᴛᴏ ᴄʀᴇᴀᴛᴇ.
• /topicdel*:* ᴅᴇʟᴇᴛᴇ ᴀɴ ᴇxɪsᴛɪɴɢ ᴛᴏᴘɪᴄ, ʀᴇǫᴜɪʀᴇs ᴛᴏᴘɪᴄ ID ᴛᴏ ᴅᴇʟᴇᴛᴇ.  
• /topicclose*:* ᴄʟᴏsᴇ ᴀɴ ᴇxɪsᴛɪɴɢ ᴛᴏᴘɪᴄ, ʀᴇǫᴜɪʀᴇs ᴛᴏᴘɪᴄ ID ᴛᴏ ᴄʟᴏsᴇ.
• /topicopen*:* ᴏᴘᴇɴ ᴀɴ ᴀʟʀᴇᴀᴅʏ ᴄʟᴏsᴇᴅ ᴛᴏᴘɪᴄ, ʀᴇǫᴜɪʀᴇs ᴛᴏᴘɪᴄ ID ᴛᴏ ᴏᴘᴇɴ.  
"""

# • /setactiontopic*:* sᴇᴛ ɪssᴜɪɴɢ ᴛᴏᴘɪᴄ ғᴏʀ ᴀᴄᴛɪᴏɴ ᴍᴇssᴀɢᴇs sᴜᴄʜ ᴀs ᴡᴇʟᴄᴏᴍᴇ, ɢᴏᴏᴅʙʏᴇ, ᴡᴀʀɴs, ʙᴀɴs,..ᴇᴛᴄ
# • /delactiontopic*:* ᴅᴇʟᴇᴛᴇ ᴅᴇғᴀᴜʟᴛ ᴛᴏᴘɪᴄ ғᴏʀ ᴀᴄᴛɪᴏɴs ᴍᴇssᴀɢᴇs.


# SET_TOPIC_HANDLER = CommandHandler("setactiontopic", set_topic_action, block=False)
# DEL_TOPIC_HANDLER = CommandHandler("delactiontopic", del_topic_action, block=False)
CREATE_TOPIC_HANDLER = CommandHandler("topicnew", create_topic, block=False)
DELETE_TOPIC_HANDLER = CommandHandler("topicdel", delete_topic, block=False)
CLOSE_TOPIC_HANDLER = CommandHandler("topicclose", close_topic, block=False)
OPEN_TOPIC_HANDLER = CommandHandler("topicopen", open_topic, block=False)

# application.add_handler(SET_TOPIC_HANDLER)
# application.add_handler(DEL_TOPIC_HANDLER)
application.add_handler(CREATE_TOPIC_HANDLER)
application.add_handler(DELETE_TOPIC_HANDLER)
application.add_handler(CLOSE_TOPIC_HANDLER)
application.add_handler(OPEN_TOPIC_HANDLER)


__command_list__ = [
    "setactiontopic",
    "delactiontopic",
    "topicnew",
    "topicclose",
    "topicopen",
]

__handlers__ = [
    # SET_TOPIC_HANDLER,
    # DEL_TOPIC_HANDLER,
    CREATE_TOPIC_HANDLER,
    DELETE_TOPIC_HANDLER,
    CLOSE_TOPIC_HANDLER,
    OPEN_TOPIC_HANDLER,
]
