from modules.core.queues import *
from telegram import *
from telegram.ext import *
from modules.core.commands import *
import asyncio
import openai
import httpx
 #Seconds
TOKEN               = os.getenv("TOKEN")
API_HASH            = os.getenv("API_HASH")
OPEN_AI_API_KEY     = os.getenv("OPEN_AI")

API_ID              = int(os.getenv("API_ID"))
FUSE_GROUP_ID       =  None #Ignored if fuse off
ADMINS_ID           = []
DEBUG_ID            = []
PROXY          = "http://127.0.0.1:8118" 
actions             =  MessageQueue()  #Queues with  messages
runner              = Pool()

model = None
if OPEN_AI_API_KEY != None:
    model = openai.OpenAI(api_key=OPEN_AI_API_KEY,http_client=httpx.Client(proxy=PROXY))



print(model)

commands            = {
    "/start": start,
    "/help": help_bot,
    "/upload": upload,
    "/kill": kill,
    "/ls": ls,
    "/mkdir": mkdir,
    "/rm": rm,
    "/ren": ren,
    "/comp": comp,
    "/size": size
}

COMMANDS = [
    "/start",
    "/help",
    "/upload"
    "/stats"
]


bot = Application.builder().token(TOKEN).build()
sender = bot.bot

runner.run()