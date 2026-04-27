from .fsinfo import *

class folder(fsinfo):
    def __init__(self,name, parent = None, fold = None, files=None):
        self.name              = name
        self.type              = DIR
        self.fold:list[folder] = fold  if fold  != None else []
        self.files:list        = files if files != None else []
        self.parent            = parent
        
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
        return 
    
    def __dict__(self):
        out = {
            "files":[],
            "folders":[],
            "name": self.name
        }
        for fold in self.fold:
            out["folders"].append(fold.__dict__())

        for files in self.files:
            out["files"].append(files.__dict__())

        return out


    def push_file(self,fil):
        self.files.append(fil)

    def pop_file(self,idx):
        return self.files.pop(idx)
    
    def ListDir(self):
        dirs = []
        for fold in self.fold:
            dirs.append(fold.name)

        for files in self.files:
            dirs.append(files.name)

        return self.ListDir()


    def CreateDirectory(self, name):
        fold            = folder(name)
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