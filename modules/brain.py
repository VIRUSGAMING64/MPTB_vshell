from modules.core.commands import *
from modules.gvar import *
from modules.chatgpt import *
from telegram import *
from modules.entity import *
from modules.utils import _parse

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
        mess:Message=await_exec(message.reply_text,["Downloading media..."])
        user = base.get(message.from_user.id)
        dlbot.download_media(message=pyrom(message),progress=progress,progress_args=[0,mess,"downloading... "],file_name=user.path + "/")
        await_exec(mess.edit_text, ["Media downloaded !!!"])       
    print(id)



def only_url(message):
    if message == None: return
    await_exec(message.reply_text,["sorry not implemented"])




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

th.Thread(target=mainloop).start()