from modules.core.queues import *
from telegram import *
from telegram.ext import *
from modules.core.commands import *
import asyncio
 #Seconds
TOKEN               = os.getenv("TOKEN")
API_HASH            = os.getenv("API_HASH")
API_ID              = int(os.getenv("API_ID"))
FUSE_GROUP_ID       =  None #Ignored if fuse off
ADMINS_ID           = []
DEBUG_ID            = []
actions             =  MessageQueue()  #Queues with  messages
runner              = Pool()



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
runner.run()