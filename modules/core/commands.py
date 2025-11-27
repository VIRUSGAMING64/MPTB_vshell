from platform import python_branch
from posixpath import dirname
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
    user = message.from_user
    user:peer = base.get(user.id)
    t_dirs = os.listdir(user.path)
    files = []
    dirs = []
    for pth in t_dirs:
        if os.path.isdir(user.path+"/"+pth):
            dirs.append(pth)
        else:
            files.append(pth)
    s:str = " " * 5 + f"[content in {user.path}]" + " " * 5 + "\n"
    for pth in dirs:
        s += F"{emojis.FILE_FOLDER} - {pth}\n"
    for pth in files:
        s += F"{emojis.LINKED_PAPERCLIPS} - {pth}\n"
    await_exec(message.reply_text, [s]) 

def rm(message:Message):
    args = message.text
    args:str = args.removeprefix("/rm ")
    user = base.get(message.from_user.id)
    if args.isnumeric():
        args = int2path(int(args),user)
        if args == None:
            await_exec(message.reply_text, ["index not found"])
            return
    
    args = user.path + "/" + args

    if not os.path.exists(args):
        await_exec(message.reply_text, ["path not found"])
        return
    p = 0
    if os.path.isdir(args):
        os.removedirs(args)
        p = 1
    else:
        p = 2
        os.remove(args)
    a = ["path","folder","file"]
    await_exec(message.reply_text, [f"{a[p]} removed"])
    ls(message)


def mkdir(message:Message):
    dirname = message.text.removeprefix("/mkdir").split()
    user = base.get(message.from_user.id)
    if len(dirname) == 0:
        await_exec(message.reply_text, ["send a valid directory name"])
        return 
    dirname = dirname[0]
    newdir = user.path + "/" + dirname
    try:
        os.mkdir(newdir)
    except Exception as e:
        await_exec(message.reply_text, [f"error making dir {str(e)}"])
    await_exec(message.reply_text, [f"directory {dirname} created"])            
    

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
    user = base.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"])
    mess =  message.text
    mess = mess.removeprefix("/su_state ").split()
    ok = len(mess) >= 2
    for i in range(mess): 
        if not mess[i].isnumeric(): 
            ok = False
        else:
            mess[i] = int(mess[i])
    if not ok:
        await_exec(message.reply_text,["send a valid user ID and valid STATE"])
        return
    
    user2 = base.get(mess[0])
    if user2 == None:
        user2 = newuser(mess[0])
    user2.state |= mess[1]
    await_exec(message.reply_text,["State of user [ok]"])

def banuser(message:Message):
    user = base.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"])
    mess =  message.text
    mess = mess.removeprefix("/banuser ")
    if not mess.isnumeric():
        await_exec(message.reply_text,["send a valid user ID"])
    id = int(mess)
    user2 = base.get(id)
    if user2 == None:
        user2 = newuser(id)
    user2.state |= BANNED
    await_exec(message.reply_text,[f"User [{id}] is banned"])


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