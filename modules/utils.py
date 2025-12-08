from operator import is_
import pyrogram.emoji as emojis
from telegram import *
from modules.core.enums import *
import asyncio
import threading as th
from modules.entity import *
import time

loop = asyncio.new_event_loop()
def loop_runner():
    global loop
    asyncio.set_event_loop(loop)
    loop.run_forever()


th.Thread(target=loop_runner, daemon=True).start()


def progress(count, total,base = "", speed = None, label = "Downloading"):
    base += f"{label}\n"
    por = ((count * 100) // total) // 10
    color = emojis.RED_CIRCLE
    if por > 3:
        color = emojis.ORANGE_CIRCLE
    if por > 6:
        color = emojis.RED_CIRCLE
    base += f"{color}" * por + f"{emojis.WHITE_CIRCLE}" * (10 - por)
    base += f" {count * 100 // total}%\n"
    if speed != None:
        base += f"Speed: {speed}/s"
    return base
    

def GetMedia(message:Message):
    media_type = 0
    if message.video != None:
        media_type += VIDEO
    if message.audio != None:
        media_type += AUDIO
    if message.document != None:
        media_type += DOCUMENT
    if message.photo != ():
        media_type += PHOTO
    if message.voice != None:
        media_type += VOICE
    return media_type


def t_user2peer(us:User):
    pw = peer()
    pw.bot_premium = 0
    pw.id = us.id
    pw.is_premium = us.is_premium
    if pw.is_premium == None:
        pw.is_premium = 0
    pw.name = us.username
    pw.path = f"env/{pw.name}-{pw.id}"
    pw.state = 0
    return pw


def await_exec(func,args):
    global loop
    fut = asyncio.run_coroutine_threadsafe(
        func(*args), loop
    )
    while fut.running():
        time.sleep(0.1)
        print("awaiting...")
    return fut._result

def getfullpath(args:str):
    assert 0


def int2path(idx,user):
    t_dirs = os.listdir(user.path)
    files = []
    t_dirs = []
    for pth in t_dirs:
        if os.path.isdir(pth):
            t_dirs.append(pth)
        else:
            files.append(pth)
    dirs = []
    for i in t_dirs:
        dirs.append(i)
    for i in files:
        dirs.append(files)
    
    if idx < 0 or idx >= len(dirs):
        return None
    
    return dirs[idx]

def newuser(id):
    user2 = peer()
    user2.bot_premium = 0
    user2.id = id
    user2.name = "..."
    user2.path = f"env/tmp-{id}"
    user2.is_premium = 0
    user2.state = 0
    try:
        os.mkdir(user2.path)
    except:
        pass 
    return user2