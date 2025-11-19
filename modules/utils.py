import pyrogram.emoji as emojis
from telegram import *
from modules.core.enums import *

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

def getfullpath(args:str):
    assert 0