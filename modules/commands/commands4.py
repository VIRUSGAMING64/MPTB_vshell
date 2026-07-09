import json
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


def allrm(message:Message, command:str):
    command = command.removeprefix("/allrm ")
    user = base.get(message.from_user.id)
    for i in os.listdir(user.path):
        di = user.path +"/"+ i
        if os.path.isfile(di):
            os.remove(di)
        else:
            os.removedirs(di)
    
    await_exec(
        message.reply_text,
        ["All files removeds"],
        bot.bot_data["bot_loop"]
    )


def splitcmd(message:Message, command:str):
    """Comando /split <filename> — divide un video en partes de 200MB y añade las partes a la cola de compresión web.
    Uso en el bot: /split path/to/video.mp4
    """
    command = command.removeprefix('/split ').strip()
    user = base.get(message.from_user.id)
    if user is None:
        await_exec(message.reply_text,["Usuario no encontrado"], bot.bot_data['bot_loop'])
        return

    infile = os.path.join(user.path, command) if not os.path.isabs(command) else command
    if not os.path.isfile(infile):
        await_exec(message.reply_text,[f"Archivo no encontrado: {infile}"], bot.bot_data['bot_loop'])
        return

    try:
        from modules.utils.videospliter import VideoSplitter
        vs = VideoSplitter(max_threads=2)
        parts = vs.split(infile, size=200, delete_original=False, verify=True)
    except Exception as e:
        await_exec(message.reply_text,[f"Error al partir: {e}"], bot.bot_data['bot_loop'])
        return

    added = 0
    for p in parts:
        try:
            # Añadir tarea al pool local 'runner' para comprimir la parte
            runner.add(lambda p=p: VideoCompressor(p, update_stat, parse_end=True).compress(), None)
            added += 1
        except Exception:
            try:
                ok, msg = queue_manager.add_task(p, update_stat)
                if ok:
                    added += 1
            except Exception:
                pass

    await_exec(message.reply_text,[f"Split completado: {len(parts)} partes. {added} añadidas a la cola."], bot.bot_data['bot_loop'])
