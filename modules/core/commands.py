from modules.core.queues import *
from modules.gvar import *
import os
from modules.utils import *
import asyncio
import threading as th
from modules.fuse import *

def start(message:Message):
    global loop
    asyncio.run_coroutine_threadsafe(message.reply_text("Hello! I am your bot. How can I assist you today?"),loop)


def kill(message:Message):
    global ADMINS_ID
    if not message.from_user.id in ADMINS_ID:
        message.reply_text("operation not available")
        return
    message.reply_text("Shutting down... Goodbye!")
    os._exit(0)

def getid(message:Message):
    await_exec(message.reply_text,[f"Your ID: {message.from_user.id}"])

def help_bot(message:Message): 
    global loop
    asyncio.run_coroutine_threadsafe(message.reply_text("Hello! I am your bot. [work in progress]"),loop)

def ls(message:Message):
    args = message.text.removeprefix("/ls")
    user = message.from_user
    user:peer = database.get(user.id)
    t_dirs = os.listdir(user.path)
    files = []
    dirs = []
    for pth in t_dirs:
        if os.path.isdir(pth):
            dirs.append(pth)
        else:
            files.append(pth)
    s:str = " " * 5 + f"[content in {user.path}]" + " " * 5
    for pth in dirs:
        s += F"{emojis.FILE_FOLDER} - {pth}"
    for pth in files:
        s += F"{emojis.LINKED_PAPERCLIPS} - {pth}"

    await_exec(message.reply_text, [s]) 

def rm(message:Message):
    args = message.text
    args:str = args.removeprefix("/rm ")
    user = database.get(message.from_user.id)
    if args.isnumeric():
        args = int2path(int(args),user)
        if args == None:
            await_exec(message.reply_text, ["index not found"])
            return
    
    if not os.path.exists(args):
        await_exec(message.reply_text, ["path not found"])
    
    p = 0
    if os.path.isdir(args):
        os.removedirs(args)
        p = 1
    else:
        p = 2
        os.remove(args)
    a = ["path","folder","file"]
    await_exec(message.reply_text, [f"{a[p]} removed"])

def mkdir(message:Message):
    args = message.text
    user = database.get(message.from_user.id)



def upload(message:Message):
    args = message.text
    file = getfullpath(args)

def ren(message:Message):
    args = message.text

def size(message:Message):
    args = message.text

def comp(message:Message):
    args = message.text

def su_state(message:Message):
    user = database.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"])
    

def banuser(message:Message):
    user = database.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"])


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
    "/size": size,
    "/getid": getid,
    "/su_state": su_state,
    "/banuser": banuser
}

COMMANDS = commands.keys()