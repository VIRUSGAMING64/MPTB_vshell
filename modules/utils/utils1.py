
from datetime import datetime
import pyrogram.emoji as emojis
from telegram import *
from modules.core.enums import *
import asyncio
from modules.entity import *
import time
from modules.gvar import *


def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    units = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}B"


def split_path(target_path, chunks_sizes):
    i = 0
    with open(target_path, 'rb') as f:
        l = 0
        chunk = ""
        while True:
            if l + 64 * 1024 <= chunks_sizes:
                chunk = f.read(64 * 1024)
                l += 64 * 1024
            else:
                chunk = f.read(chunks_sizes - l)
                l = chunks_sizes

            if not chunk:
                break

            part_filename = f"{target_path}.{str(i + 1).zfill(3)}"
            with open(part_filename, 'ab') as part_file:
                part_file.write(chunk)
            if l == chunks_sizes:
                l = 0
                i+= 1            
            
        i += 1
    return i


def time_formatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s") if seconds else "")
    return tmp.strip().strip(",")


def progress(count, total, speed = None, message:Message = None, label = "Downloading"):
    
    print("progress called")
    if datetime.now().second % 2 == 0:
        return  
    
    percentage = count * 100 / total if total > 0 else 0
    
    por = percentage / 10
    color = emojis.RED_CIRCLE
    if por > 4:
        color = emojis.ORANGE_CIRCLE
    if por > 7:
        color = emojis.GREEN_CIRCLE
    
    filled = int(por)
    bar = f"{color}" * filled + f"{emojis.WHITE_CIRCLE}" * (10 - filled)
    
    current = humanbytes(count)
    tot = humanbytes(total)

    speed_text = ""
    eta_text = ""
    if speed:
        try:
            spd_val = float(speed)
            speed_text = f"{humanbytes(spd_val)}/s"
            if spd_val > 0 and total > 0:
                remain = total - count
                eta = remain / spd_val
                eta_text = f" | ⏳ {time_formatter(int(eta))}"
        except (ValueError, TypeError):
            speed_text = f"{speed}/s"

    progtext = f"{label}\n"
    progtext += f"{bar} {percentage:.2f}%\n"
    progtext += f"⚡ {current} / {tot}\n"
    if speed_text:
        progtext += f"🚀 {speed_text}{eta_text}"
    import modules.gvar as gvar
    try:
        await_exec(
            message.edit_text, 
            [progtext], 
            gvar.bot.bot_data['bot_loop']
        )
    except Exception as e:
        print(f"Error updating progress: {e}")
    
    print(progtext)
    return progtext
    

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
    img = ["jpg","jpeg","png"]

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
