import os
from telegram import *

class peer:
    def __init__(self,_json:dict = None):
        if _json == None:
            _json = {}
        self.name        = _json.get("name")
        self.id          = _json.get("id")
        self.is_premium  = _json.get("is_premium")
        self.bot_premium = _json.get("bot_premium")
        self.path        = _json.get("path")
        self.state                   = 0
        
    def __str__(self) -> str:
        return f"{self.name},{self.id},{self.bot_premium},{self.is_premium},{self.path},{self.state}"
