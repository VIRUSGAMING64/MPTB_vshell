from modules.core.commands import *
from modules.downup import downloader
from modules.gvar import *
from modules.chatgpt import *
from telegram import *
from modules.entity import *
from modules.utils import _parse

from modules.downup.videos import *
VIDEOS_URL          = [
    ["instagram",insta_downloader],
    ["youtube", youtube_downloader],
    ["youtu.be", youtube_downloader],
    ["facebook",face_downloader]
]

def only_message(message:Message):
    if message == None:
        return
    command = message.text
    if command.startswith(BOT_HANDLER + " "):
        command = command.removeprefix(BOT_HANDLER + " ")
    
    print(f"processing message [{message.id}]")

    for com in COMMANDS:
        if message.text.startswith(com):
            commands[com](message,command)
            return
    gpt(message)        


def only_up_media(message:Message):#TODO
    if message == None:
        return
    media_type = GetMediaTypeFromFile(message)
    if media_type == VIDEO:
        pass
    elif media_type == DOCUMENT:
        pass
    elif media_type == AUDIO:
        pass
    else:
        await_exec(message.reply_text,[f"sorry not implemented fot this media type: {media_type}"], bot.bot_data["bot_loop"])
    
    await_exec(message.reply_text,["sorry not implemented"], bot.bot_data["bot_loop"])


def only_dl_media(message:Message):
    try:
        if message == None:
            return
        id = get_file_id(message)
        if id == None:
            await_exec(message.reply_text,["sorry contact with admin"])
        else:
            print("Downloading media...")
            mess:Message=await_exec(message.reply_text,["Downloading media..."], 
        bot.bot_data['bot_loop'])
            user = base.get(message.from_user.id)
            await_exec(
                dlbot.download_media,
                [
                    pyrom(message),
                    user.path + "/",
                    False,
                    True,
                    progress,
                    [0,mess,"downloading... "]
                    ],
                    dlbot.loop

            )

            await_exec(mess.edit_text, ["Media downloaded !!!"],
        bot.bot_data['bot_loop'])       
        print(id)
    except Exception as e:
        await_exec(message.reply_text,[f"error downloading media: {e}"],
        bot.bot_data['bot_loop'])


def only_url(message):
    if message == None: return
    if message.text == None: return
    url = message.text
    user = base.get(message.from_user.id)
    for name,func in VIDEOS_URL:
        if name in url:
            func(url,user,dlbot,message.chat.id,progress,[0,message,"downloading... "])
            return


    mess = await_exec(message.reply_text,[f"Starting download from url: {url}"])
    user = base.get(message.from_user.id)
    down = downloader(progress, [0,mess,"downloading... "])
    name = down.getname(url)
    down.download(url, user.path)


def main_handler():
    print("main_handler started")
    while True:
        for que in [0,1,2,3]:
            mess:Message = actions.pop(que)
            if mess == None:
                continue
            user:peer = base.get(mess.from_user.id)
            user = _parse(user,mess)
                
            if not os.path.exists(user.path):
                try:
                    os.makedirs(user.path, exist_ok=True)
                except Exception as e:
                    print(f"Error creating directory {user.path}: {e}")

            print(str(user))
            
            if user.state & BANNED:
                continue
            if que == 0:
                runner.add(only_message,[mess])
            elif que == 1:
                runner.add(only_dl_media,[mess])
            elif que == 2:
                runner.add(only_up_media,[mess])
            else:
                runner.add(only_url,[mess])
        
        time.sleep(TIMEOUT)

th.Thread(target=main_handler).start()