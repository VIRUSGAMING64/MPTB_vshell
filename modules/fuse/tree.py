
import datetime
from modules.core.enums import *
from pyrogram import Client

class fsinfo:
    name        = ""
    type        = UNKNOW
    id          = None
    parent_id   = None
    bot:Client  = None
    cache_fold  = None
    save_at     = None     #ID of group
    max_size    = 1024*1024*16#MB
    size        = 0
    created_at  = 0
    updated_at  = 0

    def check(self):
        if self.bot == None:
            raise "python bot not assigned"
        
        if self.max_size > 1024*1024*1024*2: #2GB
            raise "max size too large"

        if self.save_at == None: #2GB
            raise "save at group not assigned"



class file(fsinfo):
    def __init__(self):
        self.type    = FILE
        self.chunks  = [] #id of others chunks
        self.pointer = 0
        self.root    = 0
    
    def __str__(self):
        mess += f"{self.type},{self.name},{self.id},{self.created_at},{self.size}"
        for i in self.chunks:
            mess += f",{i}"
        return mess

    def getFileOf(self,idx):
        return idx // self.max_size

    def read(self,count):
        self.check()

    def write(self,reader):
        self.check()

    def get_size(self):
        self.check()

    def close(self):
        pass

    def save(self):
        pass


class folder(fsinfo):
    def __init__(self,base=None):
        self.base              = base
        self.type              = DIR
        self.fold:list[folder] = []
        self.files:list[file]  = []
        self.save()

    def find(self,target):
        for _curr in self.files:
            if _curr.name == target:
                return _curr
            
        for _fold in self.fold:
            if _fold.name == target:
                return _fold
            
        for fold in self.fold:
            res = fold.find(target=target)
            if res != None:
                return res
            
        return None

    def push_file(self,file):
        self.files.append(file)

    def pop_file(self,idx):
        return self.files.pop(idx)

    def CreateDirectory(self):
        fold            = folder(self.base)
        fold.bot        = self.bot
        fold.created_at = datetime.datetime.now().isoformat()
        fold.cache_fold = self.cache_fold
        fold.save_at    = self.save_at
        fold.parent_id  = self.id
        self.fold.append(fold)
        return fold

    def save(self):
        self.check()

        mess = f"{self.id}\n"
        for fil in self.files:
            if fil.id == None:
                raise "Sub file not saved"
            mess += f"{str(fil)}\n"

        for fol in self.fold:
            if fol.id == None:
                raise "sub folder not saved error"
            mess += f"{fol.type},{fol.id},{fol.name},{fol.size},{fol.parent_id}\n"
        
        #todo (use bot functions with await_exec if don't work)
        #todo (use with textfile)
        if self.id == None:
            sent = self.bot.send_message(self.save_at,mess)
            self.id = sent.message_id
        else:
            self.bot.edit_message_text(self.save_at,self.id,mess)