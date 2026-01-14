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
    res=requests.put(f"https://minube.uh.cu/public.php/dav/files/daYKRDxpKNWQARD/{command}",data=open(command,'rb'))
    await_exec(
        message.reply_text,
        [f"File uploaded with status code {res.status_code} correct: 204"],
        bot.bot_data['bot_loop']
    )