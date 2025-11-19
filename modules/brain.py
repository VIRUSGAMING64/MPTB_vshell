from modules.gvar import *
from modules.chatgpt import *
from telegram import *


def only_message(message):
    if message == None:
        return
    flag = False
    for com in COMMANDS:
        if message.text.startswith(com):
            commands[com](message)
            flag = True
    if not flag:
        gpt(message)
        
        
def only_up_media(message):
    pass


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