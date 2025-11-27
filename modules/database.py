from modules.entity import *
from modules.core.enums import *
class database:

    dic = { }

    def __init__(self,db_name="database.csv"):
        self.name = db_name
        self.load(db_name)

    def parse(self,user:peer):
        return str(user)
    
    def add(self,user:peer):
        self.dic[user.id] = user
    
    def str_user(self,data:str) -> peer:
        new = peer()
        data            = data.split(",")
        new.name        = data[USERNAME]
        new.id          = int(data[ID])
        new.bot_premium = data[BOT_PREMIUM]
        new.is_premium  = int(data[IS_PREMIUM])
        new.path        = data[PATH]
        new.state       = int(data[STATE])
        return new #! ADD STATE FIELD TO DATABASE
    
    def remove(self,user:peer):
        if self.dic.get(user.id) == None:
            return True
        del self.dic[user.id]        

    def load_str(self,data:str):
        user = self.str_user(data)
        self.add(user)

    def save(self):
        of = open(self.name,"w")
        for id in self.dic.keys():
            data = self.parse(self.dic[id])
            of.write(data + "\n")
        of.close()

    def get(self,id)->peer:
        return self.dic.get(id)

    def load(self,db_name):
        try:
            file = open(db_name)
        except:
            return
        tx = file.read(64)
        data = tx
        while tx != "":
            tx = file.read(64)
            data += tx
        data=data.split("\n")
        for raw_user in data:
            if raw_user == "":
                break
            self.load_str(raw_user)