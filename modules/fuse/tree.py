
from modules.core.enums import *

class fsinfo:
    name = ""
    type = UNKNOW

class file(fsinfo):
    def __init__(self):
        self.type = FILE

class folder(fsinfo):
    def __init__(self,base):
        self.base              = base
        self.EOF               = 0
        self.type              = DIR
        self.fold:list[folder] = []
        self.files:list[file]  = []

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

    def remove(self,target):#TODO
        try:
            for i in range(len(self.files)):
                if self.files[i].name == target:
                    self.files.pop(i)
        except:
            pass
        finally:
            pass                    

    def push_file(self,idx):
        pass

    def pop_file(self,idx):
        pass