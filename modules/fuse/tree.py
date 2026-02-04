import datetime
from operator import le

import pyrogram
from pyrogram.types import Message
from modules.core.enums import *
from pyrogram import Client

class fsinfo:
    name        = ""
    type        = UNKNOW
    id          = None
    parent_id   = None
    bot:Client  = None
    cache_fold  = None
    max_size    = 1024*1024*16#MB
    size        = 0
    created_at  = 0

    def check(self):
        if self.bot == None:
            raise "python bot not assigned"
        
        if self.max_size > 1024*1024*2000:#MB 
            raise "max size too large"

class file(fsinfo):
    def __init__(self,bot,gid,mode = "wb"):
        self.pointer  = 0
        self.root     = 0
        self.tmp_size = 0
        self.curr_id  = 0
        self.chunks   = []
        self.type     = FILE
        self.bot      = bot
        self.gid      = gid
        self.mode     = mode
        self.curr     = open("tmp",mode)

    def __str__(self):
        mess = f"{self.type},{self.name},{self.id},{self.created_at},{self.size}"
        for i in self.chunks:
            mess += f",{i}"
        return mess


    def getFileOf(self,idx):
        return idx // self.max_size


    def download(self,id):
        pass #TODO

    def read(self,count):
        self.check()
        if self.mode != "rb":
            raise "Mode error, try in another mode"
        
        R = self.getFileOf(count)

        while count > 0:
            pass #TODO


    def write(self,reader):
        self.check()
        if self.mode != "wb":
            raise "Mode error, try in another mode"
        
        if self.tmp_size + len(reader) > self.max_size:
            res = self.max_size - self.tmp_size
            self.curr.write(reader[:res])
            self.curr.close()
            self.save_file("tmp")
            self.curr = open("tmp","wb")
            wdata = reader[res:]
            self.write(wdata)
            self.size += len(wdata)
            return

        self.curr.write(reader)
        self.tmp_size += len(reader)
        self.size += len((reader))

    def save_file(self,path):
        sent:pyrogram.types.Message = self.bot.send_document(
            chat_id=self.gid,
            document=path,
            caption=f"file:{self.name},part:{len(self.chunks)+1}"
        )
        self.chunks.append(sent.id)
        self.tmp_size = 0

    def get_size(self):
        self.check()

    def close(self):
        self.curr.close()
        if self.tmp_size > 0:
            self.save_file("tmp")
        self.save()

    def save(self):
        if self.tmp_size > 0:
            raise "temp file not saved yet"
        f=open("tmp.meta","wb")
        f.write(str(self).encode())
        f.close()
        self.id = self.bot.send_document(
            chat_id=self.gid,
            document="tmp.meta",
            caption=f"file:{self.name}.meta"
        ).id

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