from platform import python_version as y

from pyrogram import __version__ as z
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import __version__ as o
from telethon import __version__ as s

from Exon import app as pbot

Chadano = "https://te.legra.ph/file/4f80999cd52a25557ae57.jpg"


@pbot.on_message(filters.command(["repo", "source"]))
async def repo(_, message):
    await message.reply_photo(
        photo=Chadano,
        caption=f"""✨ **ʜᴇʏ {message.from_user.mention},**

**ʀᴇᴘᴏ ᴏᴡɴᴇʀ  : [𝐀ʙɪꜱʜɴᴏɪ](https://t.me/plumblossomsword)**
**ᴘʏᴛʜᴏɴ ᴠᴇʀꜱɪᴏɴ :** `{y()}`
**ʟɪʙʀᴀʀʏ ᴠᴇʀꜱɪᴏɴ :** `{o}`
**ᴛᴇʟᴇᴛʜᴏɴ ᴠᴇʀꜱɪᴏɴ :** `{s}`
**ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀꜱɪᴏɴ :** `{z}`
**ʙᴏᴛ ᴠᴇʀꜱɪᴏɴ :** `2.69`
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "•ᴍᴜꜱɪᴄ•", url="https://github.com/Void-Great-Emperor/YukkiMusicBot"
                    ),
                    InlineKeyboardButton(
                        "•ᴋᴏᴍɪ•", url="https://github.com/Void-Great-Emperor/KomiShouko"
                    ),
                ]
            ]
        ),
    )
