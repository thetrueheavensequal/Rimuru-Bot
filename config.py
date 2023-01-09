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

    API_ID = int(getenv("API_ID", "24833791"))
    API_HASH = getenv("API_HASH", "42488cb247a33d13d5f97d6839c8e52b")
    TOKEN = getenv("TOKEN", "5881951624:AAE9LaaJGXbUIs_xmZGiu4pkHBWNY5_Ip-4")
    OWNER_ID = int(getenv("OWNER_ID", "2064735436"))
    OWNER_USERNAME = getenv("OWNER_USERNAME", "plumblossomsword")
    SUPPORT_CHAT = "theoneandonlymurim"
    EVENT_LOGS = int(getenv("EVENT_LOGS", "-1001859171071"))
    MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://plumblossomsword:Qn57AqxG3GRIu9IP@komi.zc6e9si.mongodb.net/?retryWrites=true&w=majority")
    DB_NAME = getenv("DB_NAME", "EXON_2")
    DATABASE_URL = getenv("DATABASE_URL", "postgresql://plumblossomsword:jmppEmTPgd5lJYoAZ039qKvxoS3hdBDI@dpg-cetvhvla4990mi84rpug-a.singapore-postgres.render.com/telegram_wbmv")

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
