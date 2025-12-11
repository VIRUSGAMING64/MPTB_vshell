from numpy import single
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
        with rq.get(url,stream=True, allow_redirects=True) as webfile:
            for chunk in webfile.iter_content(1024, False):
                data += chunk
        return data
    
    def add(self,data,file,mode = "ab"):
        file = open(file,mode)
        file.write(data)
        file.close()


    def _download(self,url, l, r, id, single = False):
        BS = 16 * 1024
        data = ""
        file = id
        while l <= r:
            if l + BS < r and l % BS == 0:
                data = self.getdata(url, l , l + BS)
                l += BS
            else:
                data = self.getdata(url, l , l)
                l += 1
            file.write(data)
            self.add(data,file)
            if single == True:
                self.call(l,r,*self.args)


    def getlenght(self,url):
        heads = rq.head(url).headers
        len = heads["Content-Length"]
        return int(len)


    def getname(self):
        raise "TODO"


    def multithread(self,url):
        return False


    def download(self, url:str): 
        len = self.getlenght(url)    
        name = self.getname(url)
        try:    
            if self.multithread(url):
                return True
            else:
                self._download(url, 0, len - 1, name, True)
                return True
        except Exception as e:
            print("download error " + str(e))
            return False