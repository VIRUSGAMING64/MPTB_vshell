from ast import Await
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

    mail_sender = MailHandler(GMAIL,GMAIL_KEY)
    try:
        mail_sender.send_file(UH_MAIL , path)
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