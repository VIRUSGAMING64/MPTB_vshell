import os
from modules.utils import *
from modules.gvar import *
import asyncio
import threading as th


def start(message:Message):
    global loop
    asyncio.run_coroutine_threadsafe(message.reply_text("Hello! I am your bot. How can I assist you today?"),loop)


def kill(message:Message):
    message.reply_text("Shutting down... Goodbye!")
    os._exit(0)


def upload(message:Message):
    args = message.text
    file = getfullpath(args)


def help_bot(message:Message): 
    global loop
    asyncio.run_coroutine_threadsafe(message.reply_text("Hello! I am your bot. [work in progress]"),loop)



def ls(message:Message):
    pass


def rm(message:Message):
    pass


def mkdir(message:Message):
    pass


def ren(message:Message):
    pass


def size(message:Message):
    pass


def comp(message:Message):
    pass