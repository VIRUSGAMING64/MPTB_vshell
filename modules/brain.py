import pyrogram
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
        return
    await_exec(message.reply_text,["sorry not implemented"])


def only_dl_media(message:Message):
    if message == None:
        return
    
    id = get_file_id(message)

    if id == None:
        await_exec(message.reply_text,["sorry not implemented contact with admin"])
    else:
        print("Downloading media...")
        mess=await_exec(message.reply_text,["Downloading media..."])
        dlbot.download_media(message=pyrom(message),progress=progress,progress_args=[0,mess,"downloading... "])
    print(id)

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
    
    if user.name == "..." and mess.from_user.username:
        user.name = mess.from_user.username
    
    user.path = f"env/{user.name}-{user.id}"
    
    if not os.path.exists(user.path):
        try:
            os.makedirs(user.path, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {user.path}: {e}")
            
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