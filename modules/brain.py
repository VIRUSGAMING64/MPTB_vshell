from modules.core.commands import *
from modules.gvar import *
from modules.chatgpt import *
from telegram import *
from modules.entity import *

def only_message(message):
    if message == None:
        return
    flag = False
    
    for com in COMMANDS:
        if message.text.startswith(com):
            commands[com](message)
            flag = True
            return
    if not flag:
        gpt(message)
        
        
def only_up_media(message):
    if message == None:
        return


def only_dl_media(message):
    if message == None:
        return


def only_url(message):
    if message == None:
        return


def mainloop():
    while True:
        for que in [0,1,2,3]:
            mess:Message = actions.pop(que)
            user = base.get(mess.id)
            if user == None:
                base.add(t_user2peer(mess.from_user))
            if que == 0:
                runner.add(only_message,[mess])
            elif que == 1:
                runner.add(only_dl_media,[mess])
            elif que == 3:
                runner.add(only_up_media,[mess])
            else:
                runner.add(only_url,[mess])
        
        time.sleep(TIMEOUT)

th.Thread(target=mainloop).start()