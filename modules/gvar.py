from telegram import *
from telegram.ext import *
import os
import openai
import httpx
from modules.database import database
 #Seconds
TOKEN               = os.getenv("TOKEN")
API_HASH            = os.getenv("API_HASH")
OPEN_AI_API_KEY     = os.getenv("OPEN_AI")
API_ID              = os.getenv("API_ID")
MANAGER_ID          = os.getenv("ADMIN")
FUSE_GROUP_ID       = None #Ignored if fuse off
ADMINS_ID           = []
DEBUG_ID            = []
PROXY_HTTP          = os.getenv("HTTP_PROXY") 
PROXY_HTTPS         = os.getenv("HTTPS_PROXY") 
DB_SAVE_TIMEOUT     = 60 #in seconds
PROXYES = {
  "http": PROXY_HTTP,
  "https": PROXY_HTTPS
}

if MANAGER_ID != None:
    if MANAGER_ID.isnumeric():
        ADMINS_ID.append(int(MANAGER_ID))
model = None

if OPEN_AI_API_KEY != None:
    model = openai.OpenAI(api_key=OPEN_AI_API_KEY,http_client=httpx.Client(proxy=PROXY_HTTP))

bot = None
sender = None
base = database()
if TOKEN != None:
    bot = Application.builder().token(TOKEN).proxy(PROXY_HTTP).build()
    sender = bot.bot
