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
            "You are not admin",
            bot.bot_data['bot_loop']
        )
        return  
    path = os.path.join(user.path,command)
    if not os.path.exists(path) or not os.path.isfile(path): 
        await_exec(
            message.reply_text,
            "File not found error",
            bot.bot_data['bot_loop']
        )
        return

    def file_iter(file_path):
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                yield chunk

    res=requests.put(f"{NEXT_CLOUD_SHARED}/{command}",data=file_iter(path),stream=True)
    await_exec(
        message.reply_text,
        [f"File uploaded with status code {res.status_code} correct: 201"],
        bot.bot_data['bot_loop']
    )