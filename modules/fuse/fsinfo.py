import datetime
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

