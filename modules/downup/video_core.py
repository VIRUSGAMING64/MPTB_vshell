from datetime import datetime
import time
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
        self._last_update = 0.0
        self._last_text = ""
        
    def my_hook(self, down:dict):
        curr = down.get("downloaded_bytes", 0)
        self.file = down.get("filename",f"{datetime.now()}.mp4")
        total = int(down.get("total_bytes",curr *2))
        total = int(down.get("total_bytes_estimate",total))
        if total <= 0:
            return

        now = time.time()
        if curr < total and (now - self._last_update) < 1.0:
            return

        text = progress(curr, total)
        
        if text == self._last_text and curr < total:
            return
        print(self.download_id)
        if self.download_id != -1:
            try:
                await_exec(
                    self.used_bot.edit_message_text,
                    [self.chat_id, self.download_id, text],
                    self.used_bot.loop
                )
                self._last_update = now
                self._last_text = text
            except Exception:
                pass

    def download_video(self, url):
        try:
            started = await_exec(
                self.used_bot.send_message,
                [self.chat_id,"Starting download"],
                self.used_bot.loop
            )
            self.download_id = getattr(started, "id", getattr(started, "message_id", started))
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
                "retries": 5,
                "fragment_retries": 5,
                "extractor_retries": 3,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
                },
                'progress_hooks': [self.my_hook],
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                if self.download_id != -1:
                    await_exec(
                        self.used_bot.edit_message_text,
                        [self.chat_id, self.download_id, "Download finished"],
                        self.used_bot.loop
                    )
            except Exception as e:
                err = str(e)
                should_retry = "Unable to extract title" in err

                if should_retry:
                    retry_opts = dict(ydl_opts)
                    retry_opts["extractor_args"] = {
                
                    }
                    try:
                        with yt_dlp.YoutubeDL(retry_opts) as ydl:
                            ydl.download([url])
                        if self.download_id != -1:
                            await_exec(
                                self.used_bot.edit_message_text,
                                [self.chat_id, self.download_id, "Download finished"],
                                self.used_bot.loop
                            )
                        self.download_id = -1
                        return
                    except Exception as retry_e:
                        err = str(retry_e)

                hint = ""

                await_exec(
                    self.used_bot.edit_message_text,
                    [self.chat_id,self.download_id,"yt-dlp error\n"+err+hint],
                    self.used_bot.loop
                )
                self.download_id = -1
        except Exception as e:
            await_exec(
                self.used_bot.edit_message_text,
                [self.chat_id,self.download_id,"error starting download\n"+str(e)],
                self.used_bot.loop
            )