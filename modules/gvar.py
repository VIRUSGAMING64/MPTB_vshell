print("initializing gvar...")
import pyrogram
from telegram import *
from telegram.ext import *
import os
import openai
import httpx
import asyncio
from modules.database import database
from modules.downup.videos import *

TOKEN               = os.getenv("TOKEN")
API_HASH            = os.getenv("API_HASH")
OPEN_AI_API_KEY     = os.getenv("OPEN_AI")
API_ID              = os.getenv("API_ID")
MANAGER_ID          = os.getenv("ADMIN")
BOT_ID              = os.getenv("BOT_ID")
PROXY_HTTP          = os.getenv("HTTP_PROXY") 
PROXY_HTTPS         = os.getenv("HTTPS_PROXY") 
BOT_HANDLER         = os.getenv("BOT_HANDLER","")

FUSE_GROUP_ID       = None #Ignored if fuse off
DB_SAVE_TIMEOUT     = 60 #in seconds

ADMINS_ID           = []
DEBUG_ID            = []

model               = None
dlbot               = None
bot                 = None
sender              = None  
main_bot_loop       = None
base                = database()


VIDEOS_URL          = [
    ["instagram",insta_downloader],
    ["youtube", youtube_downloader],
    ["facebook",face_downloader]
]

PROXYES             = {
  "http": PROXY_HTTP,
  "https": PROXY_HTTPS
}

if PROXY_HTTP == None: PROXYES = None

if MANAGER_ID != None:
    if MANAGER_ID.isnumeric():
        ADMINS_ID.append(int(MANAGER_ID))


if OPEN_AI_API_KEY != None:
    model = openai.OpenAI(api_key=OPEN_AI_API_KEY,http_client=httpx.Client(proxy=PROXY_HTTP))


async def post_init(app):
    global main_bot_loop
    app.bot_data['bot_loop'] = asyncio.get_running_loop()
    main_bot_loop = app.bot_data['bot_loop']
    print(main_bot_loop)

if TOKEN != None and API_ID != None and API_HASH != None:
    bot = Application.builder().token(TOKEN).proxy(PROXY_HTTP).post_init(post_init).build()
    sender = bot.bot
    dlbot = pyrogram.Client(
        name= "downloader",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=TOKEN
    )
else:
    raise "NO TOKEN DETECTED !!!"
