from modules.utils import *
from telegram import *
import os
import threading as th 
import multiprocessing as mp
import time

TIMEOUT             = 0.4

class Pool():
    """
    is a queue in format [function , args]
    """
    running = 0
    queue = [] 
    stop = 0
    actived = False

    def __init__(self,threads = 4):
        self.threads = threads
        self.lock = th.Lock()
        th.Thread(target = self.run).start()

    def execute(self,func,args):
        
        try:
            
            self.lock.acquire()
            self.running += 1
            self.lock.release()

            if args == None:
                func()
            func(*args)   
            
            self.lock.acquire()
            self.running -= 1
            self.lock.release()

        except Exception as e:
            raise f"Thread pool exception [{e}]" 

    def _run(self):
        while True:
            if self.threads_running() < self.threads and len(self.queue) > 0:
                
                self.lock.acquire()     
                func,args = self.queue.pop(0)
                self.lock.release()
                th.Thread(target = self.execute,args = [func,args]).start()
           
            else:
                time.sleep(TIMEOUT)
            if self.stop == 1:
                break;

    def run(self):
        if self.actived:
            return
        self.actived = True
        th.Thread(target=self._run,daemon=True).start()
    
    def destroy(self):
        self.stop = 1  

    def add(self,func,args:list):
        self.lock.acquire()  
        self.queue.append([func,args])
        self.lock.release()

    def threads_running(self):
        self.lock.acquire()
        t = self.running
        self.lock.release()
        return t


class MessageQueue():
    messages:list[Message]           = []
    download_media:list[Message]     = []
    upload_media:list[Message]       = []
    url:list[Message]                = []

    def __init__(self):
        pass

    def push(self,message:Message):
        media_type = GetMedia(message)

        if media_type != 0:
            self.download_media.append(message)
            return

        if message.text == None:
            return

        if message.text.startswith("http://") or message.text.startswith("https://"):
            self.url.append(message)
            return
        
        print("pushed message")
        self.messages.append(message)

    def pop(self,queue_index):
        """[0]messages
           [1]download_media
           [2]upload_media
           [3]url"""
        if queue_index == 0:
            if len(self.messages) == 0:
                return None
            return self.messages.pop(0)
        
        elif queue_index == 1:
            if len(self.download_media) == 0:
                return None
            return self.download_media.pop(0)

        elif queue_index == 2:
            if len(self.upload_media) == 0:
                return None
            return self.upload_media.pop(0)

        elif queue_index == 3:
            if len(self.url) == 0:
                return None
            return self.url.pop(0)
        
        return None
        

actions             =  MessageQueue()  #Queues with  messages
runner              = Pool(128)

runner.run()
