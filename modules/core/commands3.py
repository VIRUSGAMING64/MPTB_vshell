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

def put(message:Message,command:str):
    command = command.removeprefix('/put ')
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

    def file_iter(file_path):
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024*1024 * 16):
                yield chunk

    res=requests.put(f"{NEXT_CLOUD_SHARED}/{command}",data=file_iter(path))
    await_exec(
        message.reply_text,
        [f"File uploaded with status code {res.status_code} correct: 201"],
        bot.bot_data['bot_loop']
    )
    if int(res.status_code) == 201:
        return 
    await_exec(
        message.reply_text,
        [response_to_json(res)],
        bot.bot_data['bot_loop']
    )

def split(message:Message, command:str):
    command = command.removeprefix('/split ')
    user    = base.get(message.from_user.id)
    try:
        name    = command.rsplit(" ",1)[0]
        size_mb = command.rsplit(" ",1)[1]
    except Exception as e:
        await_exec(
            message.reply_text,
            ["Usage: /split filename size_in_mb"],
            bot.bot_data['bot_loop']
        )
        return
    
    if not size_mb.isnumeric():
        await_exec(
            message.reply_text,
            ["size must be a number in mb"],
            bot.bot_data['bot_loop']
        )
        return 
    size_bytes = int(size_mb) * 1024 * 1024
    if size_bytes <= 0 or size_bytes > 2000*1024*1024:
        await_exec(
            message.reply_text,
            ["size must be greater than 0 and in less than 2000 mb"],
            bot.bot_data['bot_loop']
        )
        return
    
    target_path = os.path.join(user.path, name)
    print(target_path)
    if not os.path.exists(target_path) or not os.path.isfile(target_path):
        await_exec(
            message.reply_text,
            ["file not found"],
            bot.bot_data['bot_loop']
        )
        return
    i = 0
    try:
        with open(target_path, 'rb') as f:
            l = 0
            chunk = ""
            while True:
                if l + 64 * 1024 <= size_bytes:
                    chunk = f.read(64 * 1024)
                    l += 64 * 1024
                else:
                    chunk = f.read(size_bytes - l)
                    l = size_bytes

                if not chunk:
                    break

                part_filename = f"{target_path}.{str(i).zfill(3)}"
                with open(part_filename, 'ab') as part_file:
                    part_file.write(chunk)
                if l == size_bytes:
                    l = 0
                    i+= 1            
                
            i += 1

        await_exec(
            message.reply_text,
            [f"File split into {i} parts."],
            bot.bot_data['bot_loop']
        )
    except Exception as e:
        await_exec(
            message.reply_text,
            [f"Error during splitting: {e}"],
            bot.bot_data['bot_loop']
        )


def load_cookie(message:Message, command:str):
    command = command.removeprefix('/load_cookie ')
    user = base.get(message.from_user.id)
    if user.state & ADMIN == 0:
        await_exec(
            message.reply_text,
            ["You are not admin"],
            bot.bot_data['bot_loop']
        )
        return
    path = os.path.join(user.path, command)
    if not os.path.exists(path) or not os.path.isfile(path):
        await_exec(
            message.reply_text,
            ["File not found"],
            bot.bot_data['bot_loop']
        )
        return
    try:
        with open(path, 'r') as f:
            cookies = f.read()
            global YTDLP_COOKIES
            YTDLP_COOKIES = cookies
            
        await_exec(
            message.reply_text,
            ["Cookie loaded successfully"],
            bot.bot_data['bot_loop']
        )
    except Exception as e:
        await_exec(
            message.reply_text,
            [f"Error loading cookie: {e}"],
            bot.bot_data['bot_loop']
        )




def ren(message:Message, command:str):
    command = command.removeprefix('/ren ')
    user = base.get(message.from_user.id)
