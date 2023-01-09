from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes, filters

from Exon import application
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import check_admin

MARKDOWN_HELP = f"""
ᴍᴀʀᴋᴅᴏᴡɴ ɪs ᴀ ᴠᴇʀʏ ᴘᴏᴡᴇʀғᴜʟ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴛᴏᴏʟ sᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ. {application.bot.first_name} ʜᴀs sᴏᴍᴇ ᴇɴʜᴀɴᴄᴇᴍᴇɴᴛs, ᴛᴏ ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴀᴛ \
sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴀʀᴇ ᴄᴏʀʀᴇᴄᴛʟʏ ᴘᴀʀsᴇᴅ, ᴀɴᴅ ᴛᴏ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴄʀᴇᴀᴛᴇ buttons.

• <code>_ɪᴛᴀʟɪᴄ_</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '_'  ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ɪᴛᴀʟɪᴄ ᴛᴇxᴛ
• <code>*ʙᴏʟᴅ*</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '*'  ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ʙᴏʟᴅ ᴛᴇxᴛ
• <code>`ᴄᴏᴅᴇ`</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '`'  ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ᴍᴏɴᴏsᴘᴀᴄᴇᴅ ᴛᴇxᴛ, ᴀʟsᴏ ᴋɴᴏᴡɴ ᴀs 'ᴄᴏᴅᴇ
• <code>||sᴘᴏɪʟᴇʀ||</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ `||` ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ sᴘᴏɪʟᴇʀ ᴛᴇxᴛ.
• <code>[sᴏᴍᴇᴛᴇxᴛ](t.me/plumblossomsword)</code>: ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ ʟɪɴᴋ - ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ᴊᴜsᴛ sʜᴏᴡ <code>sᴏᴍᴇᴛᴇxᴛ</code>, \
ᴀɴᴅ ᴛᴀᴘᴘɪɴɢ ᴏɴ ɪᴛ ᴡɪʟʟ ᴏᴘᴇɴ the ᴘᴀɢᴇ ᴀᴛ <code>sᴏᴍᴇᴜʀʟ</code>.

<b>ᴇxᴀᴍᴘʟᴇ:</b><code>[ᴛᴇsᴛ](example.com)</code>

• <code>[ʙᴜᴛᴛᴏɴᴛᴇxᴛ](buttonurl:someURL)</code>: ᴛʜɪs ɪs ᴀ sᴘᴇᴄɪᴀʟ ᴇɴʜᴀɴᴄᴇᴍᴇɴᴛ ᴛᴏ ᴀʟʟᴏᴡ ᴜsᴇʀs ᴛᴏ ʜᴀᴠᴇ ᴛᴇʟᴇɢʀᴀᴍ \
ʙᴜᴛᴛᴏɴs ɪɴ ᴛʜᴇɪʀ ᴍᴀʀᴋᴅᴏᴡɴ. <code>ʙᴜᴛᴛᴏɴᴛᴇxᴛ</code> ᴡɪʟʟ ʙᴇ ᴡʜᴀᴛ ɪs ᴅɪsᴘʟᴀʏᴇᴅ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ, ᴀɴᴅ <code>sᴏᴍᴇᴜʀʟ</code> \
ᴡɪʟʟ ʙᴇ ᴛʜᴇ ᴜʀʟ ᴡʜɪᴄʜ ɪs ᴏᴘᴇɴᴇᴅ.

<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>[ᴛʜɪs ɪs ᴀ ʙᴜᴛᴛᴏɴ](buttonurl:example.com)</code>

ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴍᴜʟᴛɪᴘʟᴇ ʙᴜᴛᴛᴏɴs ᴏɴ ᴛʜᴇ sᴀᴍᴇ ʟɪɴᴇ, ᴜsᴇ :same, ᴀs sᴜᴄʜ :

<code>[ᴏɴᴇ](buttonurl://example.com)
[ᴛᴡᴏ](buttonurl://google.com:same)</code>

ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴛᴡᴏ ʙᴜᴛᴛᴏɴs ᴏɴ ᴀ sɪɴɢʟᴇ ʟɪɴᴇ, ɪɴsᴛᴇᴀᴅ ᴏғ ᴏɴᴇ ʙᴜᴛᴛᴏɴ ᴘᴇʀ ʟɪɴᴇ.

ᴋᴇᴇᴘ ɪɴ ᴍɪɴᴅ ᴛʜᴀᴛ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ <b>ᴍᴜsᴛ</b> ᴄᴏɴᴛᴀɪɴ sᴏᴍᴇ ᴛᴇxᴛ ᴏᴛʜᴇʀ ᴛʜᴀɴ ᴊᴜsᴛ ᴀ ʙᴜᴛᴛᴏɴ!
"""


@check_admin(is_user=True)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        await message.reply_to_message.reply_text(
            args[1],
            parse_mode="MARKDOWN",
            disable_web_page_preview=True,
        )
    else:
        await message.reply_text(
            args[1],
            quote=False,
            parse_mode="MARKDOWN",
            disable_web_page_preview=True,
        )
    await message.delete()


async def markdown_help_sender(update: Update):
    await update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    await update.effective_message.reply_text(
        "ᴛʀʏ ғᴏʀᴡᴀʀᴅɪɴɢ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ, ᴀɴᴅ ʏᴏᴜ'ʟʟ sᴇᴇ, ᴀɴᴅ ᴜsᴇ #test !",
    )
    await update.effective_message.reply_text(
        "/save test ᴛʜɪs ɪs ᴀ ᴍᴀʀᴋᴅᴏᴡɴ ᴛᴇsᴛ - . _ɪᴛᴀʟɪᴄs_, *ʙᴏʟᴅ*, `ᴄᴏᴅᴇ`, ||ᴛᴇsᴛ|| "
        "[ᴜʀʟ](example.com) [ʙᴜᴛᴛᴏɴ](buttonurl:github.com) "
        "[ʙᴜᴛᴛᴏɴ2](buttonurl://google.com:same)",
    )


async def markdown_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.effective_message.reply_text(
            "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ᴍᴀʀᴋᴅᴏᴡɴ ʜᴇʟᴘ",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        ),
                    ],
                ],
            ),
        )
        return
    await markdown_help_sender(update)


__help__ = """
*ᴍᴀʀᴋᴅᴏᴡɴ ʜᴇʟᴘ:*

• /markdownhelp*:* ǫᴜɪᴄᴋ sᴜᴍᴍᴀʀʏ ᴏғ ʜᴏᴡ ᴍᴀʀᴋᴅᴏᴡɴ ᴡᴏʀᴋs ɪɴ ᴛᴇʟᴇɢʀᴀᴍ - ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴄᴀʟʟᴇᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛs
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=filters.ChatType.GROUPS, block=False
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, block=False)

application.add_handler(ECHO_HANDLER)
application.add_handler(MD_HELP_HANDLER)

__mod_name__ = "ᴇxᴛʀᴀs"
__command_list__ = ["id", "echo"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
]
