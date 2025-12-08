from modules.core.commands2 import *


def headers(message:Message):
    url = message.text.removeprefix("/headers ")
    response = requests.head(url)
    await_exec(message.reply_text,[f"Headers for {url}:\n{response.headers}"])



def start(message:Message):
    global loop
    asyncio.run_coroutine_threadsafe(message.reply_text("Hello! I am your bot. How can I assist you today?"),loop)

def kill(message:Message):
    global ADMINS_ID
    if not message.from_user.id in ADMINS_ID:
        message.reply_text("operation not available")
        return
    await_exec(message.reply_text, ["Shutting down... Goodbye!"])
    os._exit(0)

def getid(message:Message):
    await_exec(message.reply_text,[f"Your ID: {message.from_user.id}"])

def help_bot(message:Message): 
    global loop
    asyncio.run_coroutine_threadsafe(message.reply_text("Hello! I am your bot. [work in progress]"),loop)

def ls(message:Message):
    user = message.from_user
    user:peer = base.get(user.id)
    t_dirs = os.listdir(user.path)
    files = []
    dirs = []
    for pth in t_dirs:
        if os.path.isdir(user.path+"/"+pth):
            dirs.append(pth)
        else:
            files.append(pth)
    s:str = " " * 5 + f"[content in {user.path}]" + " " * 5 + "\n"
    for pth in dirs:
        s += F"{emojis.FILE_FOLDER} - {pth}\n"
    for pth in files:
        s += F"{emojis.LINKED_PAPERCLIPS} - {pth}\n"
    await_exec(message.reply_text, [s]) 

def rm(message:Message):
    args = message.text
    args:str = args.removeprefix("/rm ")
    user = base.get(message.from_user.id)
    if args.isnumeric():
        args = int2path(int(args),user)
        if args == None:
            await_exec(message.reply_text, ["index not found"])
            return
    
    args = user.path + "/" + args
    if not os.path.exists(args):
        await_exec(message.reply_text, ["path not found"])
        return
    p = 0
    if os.path.isdir(args):
        os.rmdir(args)
        p = 1
    else:
        p = 2
        os.remove(args)
    
    a = ["path","folder","file"]
    await_exec(message.reply_text, [f"{a[p]} removed"])
    ls(message)


def mkdir(message:Message):
    dirname = message.text.removeprefix("/mkdir").split()
    if "," in dirname:
        await_exec(message.reply_text, ["directory name cannot contain ','"])
        return
    user = base.get(message.from_user.id)
    if len(dirname) == 0:
        await_exec(message.reply_text, ["send a valid directory name"])
        return 
    dirname = dirname[0]
    newdir = user.path + "/" + dirname
    try:
        os.mkdir(newdir)
    except Exception as e:
        await_exec(message.reply_text, [f"error making dir {str(e)}"])
    await_exec(message.reply_text, [f"directory {dirname} created"])            
    

def size(message:Message):
    args = message.text.removeprefix('/size ')    
    user = base.get(message.from_user.id)
    if args.isnumeric():
        args = int2path(int(args),user)
        if args == None:
            await_exec(message.reply_text, ["index not found"])
            return
    args = user.path + "/" + args
    if not os.path.exists(args):
        await_exec(message.reply_text, [f"path not found {args}"])
        return
    size = os.path.getsize(args)    
    await_exec(message.reply_text,{f"the size is: {size}"})


def su_state(message:Message):
    user = base.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"])
        return
    mess =  message.text
    mess = mess.removeprefix("/su_state ").split()
    ok = len(mess) >= 2
    for i in range(mess): 
        if not mess[i].isnumeric(): 
            ok = False
        else:
            mess[i] = int(mess[i])
    if not ok:
        await_exec(message.reply_text,["send a valid user ID and valid STATE"])
        return
    
    user2 = base.get(mess[0])
    if user2 == None:
        user2 = newuser(mess[0])
    user2.state |= mess[1]
    await_exec(message.reply_text,["State of user [ok]"])

def banuser(message:Message):
    user = base.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"])
        return
    mess =  message.text
    mess = mess.removeprefix("/banuser ")
    if not mess.isnumeric():
        await_exec(message.reply_text,["send a valid user ID"])
    id = int(mess)
    user2 = base.get(id)
    if user2 == None:
        user2 = newuser(id)
    user2.state |= BANNED
    await_exec(message.reply_text,[f"User [{id}] is banned"])


def queues(message:Message):
    user = base.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"])
        return
    mes = f"""running actions: {runner.running}"""
    mes+= f"Messages: {len(actions.messages)}"
    mes+= f"Urls: {len(actions.url)}"
    mes+= f"Donwload media: {actions.download_media}"
    mes+= f"Upload: {actions.upload_media}"    

def upload(message:Message):
    message.text = message.text.removeprefix("/upload")
    await_exec(message.reply_text("Download pushed to queue"))
    actions.upload_media.append(message)


commands            = {
    "/start": start,
    "/help": help_bot,
    "/upload": upload,
    "/kill": kill,
    "/ls": ls,
    "/mkdir": mkdir,
    "/rm": rm,
    "/ren": ren,
    "/comp": comp,
    "/size": size,
    "/getid": getid,
    "/su_state": su_state,
    "/banuser": banuser,
    "/queues": queues,
    "/upload": upload,
    "/headers": headers
}

COMMANDS = commands.keys()