from modules.core.commands import *
from modules.gvar import *
from modules.chatgpt import *
from telegram import *
from modules.entity import *

def only_message(message:Message):
    if message == None:
        return
    print(f"processing message [{message.id}]")
    for com in COMMANDS:
        if message.text.startswith(com):
            commands[com](message)
            return
    gpt(message)
        
        
def only_up_media(message:Message):
    if message == None:
        returnn
    await_exec(message.reply_text,["sorry not implemented"])


def only_dl_media(message:Message):
    if message == None:
        return
    await_exec(message.reply_text,["sorry not implemented"])
    

def only_url(message):
    if message == None:
        return
    await_exec(message.reply_text,["sorry not implemented"])





def database_saver():
    while True:
        time.sleep(DB_SAVE_TIMEOUT)
        base.save()


def _parse(user:peer, mess:Message)->peer:
    if user == None:
        user = t_user2peer(mess.from_user)
        base.add(user)
        user.path = f"env/{user.name}-{user.id}"
        try:
            os.mkdir(user.path)
        except:
            pass
    if user.name == "...":
        user.name = mess.from_user.username
        user.path = f"env/{user.name}-{user.id}"
        try:
            os.mkdir(user.path)
        except:
            pass
    try:
        os.mkdir(user.path)
    except:
        pass
    return user

def mainloop():
    print("mainloop started")
    while True:
        for que in [0,1,2,3]:
            mess:Message = actions.pop(que)
            if mess == None:
                continue
            user:peer = base.get(mess.from_user.id)
            user = _parse(user,mess)
            print(str(user))
            if user.state & BANNED:
                continue
            if que == 0:
                runner.add(only_message,[mess])
            elif que == 1:
                runner.add(only_dl_media,[mess])
            elif que == 3:
                runner.add(only_up_media,[mess])
            else:
                runner.add(only_url,[mess])
        
        time.sleep(TIMEOUT)

th.Thread(target=database_saver).start()
th.Thread(target=mainloop).start()