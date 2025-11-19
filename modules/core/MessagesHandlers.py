from telegram import *
from telegram.ext import *
from modules.gvar import *

async def on_message(update:Update,context):
    message = update.message
    if message.chat.type == Chat.PRIVATE:
        direct_message(update.message)
    elif message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        group_message(message)
    elif message.chat.type == Chat.CHANNEL:
        channel_message(message)
    else:
        unknow_message(message)

def direct_message(message:Message):
    actions.push(message)

def group_message(message:Message):
    pass

def channel_message(message:Message):
    pass

def unknow_message(message:Message):
    pass