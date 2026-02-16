from modules.core.commands.commands2 import *


def headers(message:Message,command:str):
    url = command.removeprefix("/headers ").strip()
    response = requests.head(url)
    await_exec(
        message.reply_text,
        [f"Headers for {url}:\n{response.headers}"],
        bot.bot_data['bot_loop']
    )


def start(message:Message,command:str):
    await_exec(
        message.reply_text,
        ["Hello! I am your bot. How can I assist you today?"],
        bot.bot_data['bot_loop']
    )

def kill(message:Message,command:str):
    global ADMINS_ID
    if not message.from_user.id in ADMINS_ID:
        message.reply_text("operation not available")
        return
    await_exec(
        message.reply_text, 
        ["Shutting down... Goodbye!"],
        bot.bot_data['bot_loop']
    )
    os._exit(0)

def getid(message:Message,command:str):
    await_exec(message.reply_text,[f"Your ID: {message.from_user.id}"], bot.bot_data['bot_loop'])

def help_bot(message:Message,command:str): 
    await_exec(
        message.reply_text,
        ["Hello! I am your bot. [work in progress]"],
        bot.bot_data['bot_loop']
    )

def ls(message:Message,command:str):
    user = message.from_user
    user:peer = base.get(user.id)
    try:
        t_dirs = os.listdir(user.path)
    except FileNotFoundError:
        await_exec(message.reply_text, ["Directory not found"],
        bot.bot_data['bot_loop'])
        return

    files = []
    dirs = []
    
    for pth in t_dirs:
        full_path = os.path.join(user.path, pth)
        if os.path.isdir(full_path):
            dirs.append(pth)
        else:
            files.append(pth)
    s:str = " " * 5 + f"[content in {user.path}]" + " " * 5 + "\n"
    for pth in dirs:
        s += F"{emojis.FILE_FOLDER} - {pth}\n"
    for pth in files:
        s += F"{emojis.LINKED_PAPERCLIPS} - {pth}\n"
    await_exec(message.reply_text, [s], bot.bot_data['bot_loop'])

def rm(message:Message,command:str):
    args = command
    args:str = args.removeprefix("/rm ")
    user = base.get(message.from_user.id)
    if args.isnumeric():
        args = int2path(int(args),user)
        if args == None:
            await_exec(message.reply_text, ["index not found"],
        bot.bot_data['bot_loop'])
            return
    
    args = os.path.join(user.path, args)
    if not os.path.exists(args):
        await_exec(message.reply_text, ["path not found"], bot.bot_data['bot_loop'])
        return
    p = 0
    if os.path.isdir(args):
        os.rmdir(args)
        p = 1
    else:
        p = 2
        os.remove(args)
    
    a = ["path","folder","file"]
    await_exec(message.reply_text, [f"{a[p]} removed"],
        bot.bot_data['bot_loop'])
    ls(message,"/ls")


def mkdir(message:Message,command:str):
    dirname = command
    if "," in dirname:
        await_exec(message.reply_text, ["directory name cannot contain ','"],
        bot.bot_data['bot_loop'])
        return
    user = base.get(message.from_user.id)
    if len(dirname) == 0:
        await_exec(message.reply_text, ["send a valid directory name"],
        bot.bot_data['bot_loop'])
        return 
    dirname = dirname.split(" ")[1]
    newdir = os.path.realpath(user.path) + "/" + dirname
    print(user.path, dirname, command)
    try:
        print(newdir)
        os.mkdir(newdir)
    except Exception as e:
        await_exec(message.reply_text, [f"error making dir {str(e)}"], bot.bot_data['bot_loop'])
        return
    await_exec(message.reply_text, [f"directory {dirname} created"], bot.bot_data['bot_loop'])            
    

def size(message:Message,command:str):
    args = command.removeprefix("/size ")
    user = base.get(message.from_user.id)
    if args.isnumeric():
        args = int2path(int(args),user)
        if args == None:
            await_exec(message.reply_text, ["index not found"], bot.bot_data['bot_loop'])
            return
    args = user.path + "/" + args
    if not os.path.exists(args):
        await_exec(message.reply_text, [f"path not found {args}"], bot.bot_data['bot_loop'])
        return
    size = os.path.getsize(args)    
    await_exec(message.reply_text,[f"the size is: {size}"], bot.bot_data['bot_loop'])


def su_state(message:Message,command:str):
    user = base.get(message.from_user.id)
    print(user.path)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"],
        bot.bot_data['bot_loop'])
        return
    mess =  command
    mess = mess.removeprefix("/su_state ").split()
    ok = len(mess) >= 2
    for i in range(mess): 
        if not mess[i].isnumeric(): 
            ok = False
        else:
            mess[i] = int(mess[i])
    if not ok:
        await_exec(message.reply_text,["send a valid user ID and valid STATE"], bot.bot_data['bot_loop'])
        return
    
    user2 = base.get(mess[0])
    if user2 == None:
        user2 = newuser(mess[0])
    user2.state |= mess[1]
    await_exec(message.reply_text,["State of user [ok]"],
        bot.bot_data['bot_loop'])

def banuser(message:Message,command:str):
    user = base.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"], bot.bot_data['bot_loop'])
        return
    mess =  command
    mess = mess.removeprefix("/banuser ")
    if not mess.isnumeric():
        await_exec(message.reply_text,["send a valid user ID"], bot.bot_data['bot_loop'])
        return
    id = int(mess)
    user2 = base.get(id)
    if user2 == None:
        user2 = newuser(id)
    user2.state |= BANNED
    await_exec(message.reply_text,[f"User [{id}] is banned"],
        bot.bot_data['bot_loop'])


commands = {
    "/start":       start,
    "/help":        help_bot,
    "/upload":      upload,
    "/kill":        kill,
    "/ls":          ls,
    "/mkdir":       mkdir,
    "/rm":          rm,
    "/ren":         ren,
    "/comp":        comp,
    "/size":        size,
    "/getid":       getid,
    "/su_state":    su_state,
    "/banuser":     banuser,
    "/queues":      queues,
    "/upload":      upload,
    "/headers":     headers,
    "/x265":        x265,
    "/stats":       stats,
    "/cd":          cd,
    "/put":         put,
    "/split":       split,
    "/appendmail":  appendmail,
    "/mailput":     mailput,
    "/load_cookie": load_cookie

}

COMMANDS = commands.keys()