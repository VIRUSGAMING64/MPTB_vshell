from datetime import datetime
from pyrogram.client import Client
import yt_dlp
from modules.utils import *
from modules.gvar import *

class VidDownloader:
    file = ""
    arg = "downloading video"
    def __init__(self, used_bot:Client,user,chat_id,progress:callable,args:list):
        self.used_bot = used_bot
        self.user = user
        self.progress = progress
        self.args = args
        self.chat_id = chat_id
        self.file = None
        self.download_id = -1
        
    def my_hook(self, down:dict):
        curr =down.get("downloaded_bytes", 0)
        self.file = down.get("filename",f"{datetime.now()}.mp4")
        total = int(down.get("total_bytes",curr *2))
        total = int(down.get("total_bytes_estimate",total))
        self.progress(curr,total,*self.args)

    def download_video(self, url):
        try:
            self.download_id = await_exec(
                self.used_bot.send_message,
                [self.chat_id,"Starting download"],
                self.used_bot.loop
            )
            if YTDLP_COOKIES != None:
                with open("cookies.txt","w") as f:
                    f.write(YTDLP_COOKIES)
                    f.close()

            ydl_opts = {
                "paths":{
                    "home":self.user.path
                },
                "cookiefile":"cookies.txt" if YTDLP_COOKIES != None else None,
                'format': 'best',
                "writesubtitles":True,
                "subtitleslangs":["es","en"],
                'writethumbnail': True,
                'progress_hooks': [self.my_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except Exception as e:
                    await_exec(
                        self.used_bot.edit_message_text,
                        [self.chat_id,self.download_id,"unknow error\n"+str(e)],
                        self.used_bot.loop
                    )
                self.download_id = -1
        except Exception as e:
            await_exec(
                self.used_bot.edit_message_text,
                [self.chat_id,self.download_id,"error starting download\n"+str(e)],
                self.used_bot.loop
            )