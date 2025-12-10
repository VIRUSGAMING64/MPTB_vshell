from more_itertools import chunked
from modules.entity import *
from modules.gvar import *
from modules.core import *
from modules.database import *
import requests as rq
from multiprocessing import Process
from telegram.ext import *
from pyrogram import Client

from tkinter.tix import Tree

class downloader:
    def __init__(self,sender:Bot|Client, user:peer, threads = 32):
        self.sender = sender
        self.user = user
        self.threads = threads

    def update_message(self):
        pass

    def getdata(self,url,l,r) -> str:
        data = ""
        with rq.get(url,stream=True) as webfile:
            for chunck in webfile.iter_content(1024):
                data += chunck
        
        return data
    
    def save(data,file):
        pass

    def _download(self,url, l, r, id):
        BS = 16 * 1024
        data = ""
        file = open(self.save_path + "/" + str(id),"w")
        while l <= r:
            if l + BS < r and l % BS == 0:
                data = self.getdata(url, l , l + BS)
                l += BS
            else:
                data = self.getdata(url, l , l)
                l += 1
            file.write(data)
            self.save(data,file)

    def getlenght(self,url):
        heads = rq.head(url).headers
        len = heads["Content-Lenght"]
        return int(len)
    
    def multithread(self,url):
        pass

    def download(self, url:str): 
        len = self.getlenght(url)    
        
        if self.multithread(url):
            return True
        