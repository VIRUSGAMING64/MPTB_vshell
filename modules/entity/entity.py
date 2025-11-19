import os
from telegram import *

class peer(User):
    root = "env"

    def __init__(self,_json):
        self.name       = _json["name"]
        self.id         = _json["id"]
        self.is_premium = _json[""]
        
    def __str__(self):
        pass

    def is_folder(s:str):
        if os._path.exists(s):
            return s.endswith("/")
        return False    
    
