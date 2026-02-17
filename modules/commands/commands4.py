import json
from shutil import ExecError
import requests
import time
from modules.compress.comp import Tar
from modules.compress.video import VideoCompressor
from modules.core.queues import *
from modules.gvar import *
import os
import psutil
from modules.utils import *
import asyncio
import threading as th
from modules.fuse import *
from modules.core.mail import *

def mailput(message:Message,command:str):
    command = command.removeprefix('/mailput ')
    user = base.get(message.from_user.id)
    if user.state & ADMIN == 0:
        await_exec(
            message.reply_text,
            ["You are not admin"],
            bot.bot_data['bot_loop']
        )
        return  
    
    path = os.path.join(user.path,command)
    if not os.path.exists(path) or not os.path.isfile(path): 
        await_exec(
            message.reply_text,
            ["File not found error"],
            bot.bot_data['bot_loop']
        )
        return
    
    try:
        mailhand.upload(path)
    except Exception as e:
        await_exec(
            message.reply_text, 
            [f"Error sending mail: {e}"],
            bot.bot_data['bot_loop']
        )
        return 

    await_exec(
        message.reply_text, 
        ["File sent successfully"],
        bot.bot_data['bot_loop']
    )



def adduhmail(message:Message,command:str):
    global UH_MAIL
    command = command.removeprefix('/adduhmail ')
    user = base.get(message.from_user.id)
    if user.state & ADMIN == 0:
        await_exec(
            message.reply_text,
            ["You are not admin"],
            bot.bot_data['bot_loop']
        )
        return  
    
    UH_MAIL = command
    
    await_exec(
        message.reply_text,
        [f"UH Mail set to {UH_MAIL}"],
        bot.bot_data['bot_loop']
    )

def appendmail(message:Message , command : str):
    command = command.removeprefix("/appendmail ")
    user    = base.get(message.from_user.id)
    if user.state & ADMIN == 0:
        await_exec(
            message.reply_text,
            ["YOU are not admin"],
            bot.bot_data["bot_loop"]
        )
        return
    try:
        command = command.split(",")
        uhmail = command[0]
        key    = command[1] 
        mailhand.add(key,uhmail)
        await_exec(
            message.reply_text,
            [f"Mail added successfully"],
            bot.bot_data["bot_loop"]
        )    
    except Exception as e:
        await_exec(
            message.reply_text,
            [f"error adding mail [{e}]"],
            bot.bot_data["bot_loop"]
        )