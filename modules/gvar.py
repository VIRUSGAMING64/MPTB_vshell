from telegram import *
from telegram.ext import *
import os
import asyncio
import openai
import httpx
from modules.core.enums import ADMIN
from modules.database import database
 #Seconds
TOKEN               = os.getenv("TOKEN")
API_HASH            = os.getenv("API_HASH")
OPEN_AI_API_KEY     = os.getenv("OPEN_AI")
API_ID              = os.getenv("API_ID")
MANAGER_ID                     = os.getenv("ADMIN")
FUSE_GROUP_ID       =  None #Ignored if fuse off
ADMINS_ID           = []
DEBUG_ID            = []
PROXY          = "http://127.0.0.1:8118" 
DB_SAVE_TIMEOUT    = 60 #in seconds

if MANAGER_ID != None:
    if MANAGER_ID.isnumeric():
        ADMINS_ID.append(int(MANAGER_ID))
model = None
if OPEN_AI_API_KEY != None:
    model = openai.OpenAI(api_key=OPEN_AI_API_KEY,http_client=httpx.Client(proxy=PROXY))

bot = None
sender = None
base = database()
if TOKEN != None:
    bot = Application.builder().token(TOKEN).build()
    sender = bot.bot
