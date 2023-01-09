import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Exon import app as abishnoi


@abishnoi.on_message(filters.command(["imdb", "tmdb"]))
async def imdb(_, message):
    if len(message.command) < 2:
        return await message.reply_text("ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ\n\nᴇx. /imdb Kgf")
    text = (
        message.text.split(None, 1)[1]
        if len(message.command) < 3
        else message.text.split(None, 1)[1].replace(" ", "%20")
    )
    url = requests.get(f"https://api.safone.me/tmdb?query={text}").json()["results"][0]
    await message.reply_photo(
        photo=url["poster"],
        caption=f"""**ɪᴍᴅʙ ᴍᴏᴠɪᴇ ᴅᴇᴛᴀɪʟs :**

**ᴛɪᴛʟᴇ :** {url["title"]}
**ᴅᴇsᴄʀɪᴘᴛɪᴏɴ :** {url["overview"]}
**ʀᴀᴛɪɴɢ :** {url["rating"]}
**ʀᴇʟᴇᴀsᴇ-ᴅᴀᴛᴇ :** {url["releaseDate"]}
**ᴘᴏᴘᴜʟᴀʀɪᴛʏ :** {url["popularity"]}
**ʀᴜɴᴛɪᴍᴇ :** {url["runtime"]}
**sᴛᴀᴛᴜs :** {url["status"]}
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ɪᴍᴅʙ ʟɪɴᴋ",
                        url=url["imdbLink"],
                    ),
                ],
            ],
        ),
    )


__help__ = """
 ❍ /imdb <ᴍᴏᴠɪᴇ ɴᴀᴍᴇ>*:* ɢᴇᴛ ғᴜʟʟ ɪɴғᴏ ᴀʙᴏᴜᴛ ᴀ ᴍᴏᴠɪᴇ ғʀᴏᴍ [ɪᴍᴅʙ.ᴄᴏᴍ](https://m.imdb.com)
"""

__mod_name__ = "ɪᴍᴅʙ"
