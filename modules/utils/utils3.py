
from datetime import datetime
import pyrogram.emoji as emojis
from telegram import *
from modules.core.enums import *
import asyncio
from modules.entity import *
import time
from modules.gvar import *
   

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

def GetMediaTypeFromFile(message:Message):
    file = message.text.split(" ",   1)
    file = file[1]
    img = ["jpg","jpeg","png"]
    vids =["mp4", "mpg", "avi","mkv", "mpeg"]
    for i in img:
        if file.endswith(i):
            return PHOTO
    for i in vids:
        if file.endswith(i):
            return VIDEO

    return DOCUMENT

def get_file_id(message: Message):
    typ = GetMedia(message)
    if typ & DOCUMENT:
        return message.document.file_id
    elif typ & AUDIO:
        return message.audio.file_id
    elif typ & VIDEO:
        return message.video.file_id
    elif typ & PHOTO:
        return message.photo[-1].file_id
    elif typ & VOICE:
        return message.voice.file_id
    return None

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_emoji(percent):
    if percent < 60:
        return "🟢"
    elif percent < 85:
        return "🟡"
    else:
        return "🔴"
