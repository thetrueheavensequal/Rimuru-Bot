import json
import os
from os import getenv

from dotenv import load_dotenv

load_dotenv()


def get_user_list(config, key):
    with open("{}/Exon/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    LOGGER = True

    API_ID = int(getenv("API_ID", "21927988"))
    API_HASH = getenv("API_HASH", "e18f720acdff1e5b0ec80616aecd8a5ab")
    TOKEN = getenv("TOKEN", "5881951624:AAFUHAplvl5FstzQ-2uLncRthjx4tjNP_Zo")
    OWNER_ID = int(getenv("OWNER_ID", "2064735436"))
    OWNER_USERNAME = getenv("OWNER_USERNAME", "plumblossomsword")
    SUPPORT_CHAT = "theoneandonlymurim"
    EVENT_LOGS = int(getenv("EVENT_LOGS", "-1001859171071"))
    MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://plumblossomsword:Qn57AqxG3GRIu9IP@komi.zc6e9si.mongodb.net/?retryWrites=true&w=majority")
    DB_NAME = getenv("DB_NAME", "EXON_2")
    DATABASE_URL = getenv("DATABASE_URL", "postgresql://plumblossomsword:YOHMSYTKcjYLaqioWlyCDRrJZSkSmvQ3@dpg-cevf5782i3mntl1sh6q0-a.frankfurt-postgres.render.com/telegram_postgresql")

    # ɴᴏ ᴇᴅɪᴛ ᴢᴏɴᴇ
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

    LOAD = []
    NO_LOAD = ["connection"]
    BL_CHATS = []
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    DEV_USERS = get_user_list("elevated_users.json", "devs")


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
