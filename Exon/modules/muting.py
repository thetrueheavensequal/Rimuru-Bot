import html
from typing import Union

from telegram import Bot, Chat, ChatMemberRestricted, ChatPermissions, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html

from Exon import LOGGER, application
from Exon.modules.helper_funcs.chat_status import (
    check_admin,
    connection_status,
    is_user_admin,
)
from Exon.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable


async def check_user(user_id: int, bot: Bot, chat: Chat) -> Union[str, None]:
    if not user_id:
        reply = "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
        return reply

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            reply = "I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ"
            return reply
        else:
            raise

    if user_id == bot.id:
        reply = "I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ MUTE ᴍʏsᴇʟғ, ʜᴏᴡ ʜɪɢʜ ᴀʀᴇ ʏᴏᴜ?"
        return reply

    if await is_user_admin(chat, user_id, member):
        reply = "ᴄᴀɴ'ᴛ. ғɪɴᴅ sᴏᴍᴇᴏɴᴇ ᴇʟsᴇ ᴛᴏ ᴍᴜᴛᴇ ʙᴜᴛ ɴᴏᴛ ᴛʜɪs ᴏɴᴇ."
        return reply

    return None


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = await extract_user_and_text(message, context, args)
    reply = await check_user(user_id, bot, chat)

    if reply:
        await message.reply_text(reply)
        return ""

    member = await chat.get_member(user_id)

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ᴍᴜᴛᴇ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    if reason:
        log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

    if not isinstance(member, ChatMemberRestricted) and (
        member.can_send_messages if isinstance(member, ChatMemberRestricted) else None
    ):
        chat_permissions = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(chat.id, user_id, chat_permissions)
        await bot.sendMessage(
            chat.id,
            f"ᴍᴜᴛᴇᴅ <b>{html.escape(member.user.first_name)}</b> ᴡɪᴛʜ ɴᴏ ᴇxᴘɪʀᴀᴛɪᴏɴ ᴅᴀᴛᴇ!",
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )
        return log

    else:
        await message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴍᴜᴛᴇᴅ !")

    return ""


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id = await extract_user(message, context, args)
    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ'ʟʟ ɴᴇᴇᴅ ᴛᴏ ᴇɪᴛʜᴇʀ ɢɪᴠᴇ ᴍᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴛᴏ ᴜɴᴍᴜᴛᴇ, ᴏʀ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ ᴛᴏ ʙᴇ ᴜɴᴍᴜᴛᴇᴅ.",
        )
        return ""

    member = await chat.get_member(int(user_id))

    if member.status != "kicked" and member.status != "left":
        if not isinstance(member, ChatMemberRestricted):
            await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴀʟʀᴇᴀᴅʏ ʜᴀs ᴛʜᴇ ʀɪɢʜᴛ ᴛᴏ sᴘᴇᴀᴋ.")
        else:
            chat_permissions = ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
            try:
                await bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
            except BadRequest:
                pass
            await bot.sendMessage(
                chat.id,
                f"I sʜᴀʟʟ ᴀʟʟᴏᴡ <b>{html.escape(member.user.first_name)}</b> ᴛᴏ ᴛᴇxᴛ!",
                parse_mode=ParseMode.HTML,
                message_thread_id=message.message_thread_id if chat.is_forum else None,
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ᴜᴍᴜᴛᴇ\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>ᴍᴇɴᴛɪᴏɴ:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        await message.reply_text(
            "ᴛʜɪs ᴜsᴇʀ ɪsɴ'ᴛ ᴇᴠᴇɴ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ, ᴜɴᴍᴜᴛɪɴɢ ᴛʜᴇᴍ ᴡᴏɴ'ᴛ ᴍᴀᴋᴇ ᴛʜᴇᴍ ᴛᴀʟᴋ ᴍᴏʀᴇ ᴛʜᴀɴ ᴛʜᴇʏ "
            "ᴀʟʀᴇᴀᴅʏ ᴅᴏ!",
        )

    return ""


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def temp_mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = await extract_user_and_text(message, context, args)
    reply = await check_user(user_id, bot, chat)

    if reply:
        await message.reply_text(reply)
        return ""

    member = await chat.get_member(user_id)

    if not reason:
        await message.reply_text("ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴀ ᴛɪᴍᴇ ᴛᴏ ᴍᴜᴛᴇ ᴛʜɪs ᴜsᴇʀ ғᴏʀ !")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    mutetime = await extract_time(message, time_val)

    if not mutetime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ᴛᴇᴍᴘ_ɴᴜᴛᴇᴅ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>ᴛɪᴍᴇ:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

    try:
        if not isinstance(member, ChatMemberRestricted) and (
            member.can_send_messages
            if isinstance(member, ChatMemberRestricted)
            else None
        ):
            chat_permissions = ChatPermissions(can_send_messages=False)
            await bot.restrict_chat_member(
                chat.id,
                user_id,
                chat_permissions,
                until_date=mutetime,
            )
            await bot.sendMessage(
                chat.id,
                f"ᴍᴜᴛᴇᴅ <b>{html.escape(member.user.first_name)}</b> for {time_val}!",
                parse_mode=ParseMode.HTML,
                message_thread_id=message.message_thread_id if chat.is_forum else None,
            )
            return log
        else:
            await message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴍᴜᴛᴇᴅ.")

    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            await message.reply_text(f"ᴍᴜᴛᴇᴅ ғᴏʀ {time_val}!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴍᴜᴛɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴍᴜᴛᴇ ᴛʜᴀᴛ ᴜsᴇʀ.")

    return ""


__help__ = """
*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• /mute <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* sɪʟᴇɴᴄᴇs ᴀ ᴜsᴇʀ. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ, ᴍᴜᴛɪɴɢ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴜsᴇʀ.
• /tmute <ᴜsᴇʀʜᴀɴᴅʟᴇ> x(ᴍ/ʜ/ᴅ)`*:* ᴍᴜᴛᴇs ᴀ ᴜsᴇʀ for x ᴛɪᴍᴇ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ reply). `m` = `ᴍɪɴᴜᴛᴇs`, `h` = `ʜᴏᴜʀs`, `d` = `ᴅᴀʏs`.
• /unmute <ᴜsᴇʀʜᴀɴᴅʟᴇ>`*:* ᴜɴᴍᴜᴛᴇs ᴀ ᴜsᴇʀ. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ, ᴍᴜᴛɪɴɢ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴜsᴇʀ.
"""

MUTE_HANDLER = CommandHandler("mute", mute, block=False)
UNMUTE_HANDLER = CommandHandler("unmute", unmute, block=False)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute, block=False)

application.add_handler(MUTE_HANDLER)
application.add_handler(UNMUTE_HANDLER)
application.add_handler(TEMPMUTE_HANDLER)

__mod_name__ = "ᴍᴜᴛɪɴɢ"
__handlers__ = [MUTE_HANDLER, UNMUTE_HANDLER, TEMPMUTE_HANDLER]
