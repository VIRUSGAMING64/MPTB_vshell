from modules.entity import *
from modules.gvar import *
from modules.core import *
from modules.database import *
import requests as rq
from telegram.ext import *
from pyrogram import Client

class downloader:
    def __init__(self,progress =  None,args = [],threads = 4):
        self.threads = threads
        if progress == None:
            progress = self.__call
        self.call = progress
        self.args = args

    def __call(self):
        pass

    def getdata(self,url,l,r) -> bytes:
        data = b""
        headers = {"Range":f"bytes={l}-{r}"}
        resp = rq.get(url,headers=headers,stream=True)
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                data += chunk

        return data
    
    def add(self,data,file,mode = "ab"):
        file = open(file,mode)
        file.write(data)
        file.close()

    def _download(self,url, l, r, filename, single = False):
        BS = 1024*1024
        data = ""
        while l <= r:
            print(l)
            data = self.getdata(url, l , l + BS)
            l += BS
            self.add(data,filename)
            if single == True:
                self.call(l,r,*self.args)


    def getlenght(self,url) -> int:
        heads = rq.head(url).headers
        len = heads["Content-Length"]
        return int(len)


    def getname(self,url) -> str:
        if not "/" in url:
            return "unnamed.file" 
        url = url.rsplit("/",1)[1]
        return url

    def multithread(self,url) -> bool:
        return False

    def download(self, url:str, save_folder:str = "") -> bool: 
        len = self.getlenght(url)    
        name = save_folder + "/" +self.getname(url)
        try:    
            if self.multithread(url):
                return True
            else:
                self._download(url, 0, len - 1, name, True)
                return True
        except Exception as e:
            print("download error " + str(e))
            return False