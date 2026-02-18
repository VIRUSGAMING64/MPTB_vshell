from pyrogram.client import Client

if fsinfo == None:
    from .file import *
    from .folder import *

def download(message,bot:Client,save = "downloads/"):
    bot.download_media(message,save)


def GetHandler(message:Message,bot:Client):
    obj  = bot.download_media(message, in_memory=True)
    data = bytes(obj.getbuffer())
    data = data.split(",")
    hand = None

    for i in range(len(data)):
        if str(data[i]).isnumeric():
            data[i] = int(data[i])

    if data[0] == DIR:
        hand = folder()
    else:
        hand        = file()
        hand.chunks = []
        for i in range(6,len(data)):
            hand.chunks.append(data[i])

        hand.size = data[5]

    hand.name       = data[1]
    hand.id         = data[2]
    hand.created_at = data[3]
    hand.name       = data[4] 

    return hand