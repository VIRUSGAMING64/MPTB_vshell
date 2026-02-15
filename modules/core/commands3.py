from modules.core.commands4 import *

def put(message:Message,command:str):
    command = command.removeprefix('/put ')
    user = base.get(message.from_user.id)
    if user.state & ADMIN == 0:
        await_exec(
            message.reply_text,
            ["You are not admin"],
            bot.bot_data['bot_loop']
        )
        return  
    path = os.path.join(user.path,command)
    if not os.path.exists(path) or not os.path.isfile(path): 
        await_exec(
            message.reply_text,
            ["File not found error"],
            bot.bot_data['bot_loop']
        )
        return

    def file_iter(file_path):
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024*1024 * 16):
                yield chunk

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    }
    res=requests.put(f"{NEXT_CLOUD_SHARED}/{command}",data=file_iter(path), headers=headers)
    await_exec(
        message.reply_text,
        [f"File uploaded with status code {res.status_code} correct: 201"],
        bot.bot_data['bot_loop']
    )
    if int(res.status_code) == 201:
        return 
    await_exec(
        message.reply_text,
        [response_to_json(res)],
        bot.bot_data['bot_loop']
    )

def split(message:Message, command:str):
    command = command.removeprefix('/split ')
    user    = base.get(message.from_user.id)
    try:
        name    = command.rsplit(" ",1)[0]
        size_mb = command.rsplit(" ",1)[1]
        if not size_mb.isnumeric():
            await_exec(
                message.reply_text,
                ["size must be a number in mb"],
                bot.bot_data['bot_loop']
            )
            raise "Not numeric size"
    except Exception as e:
        await_exec(
            message.reply_text,
            ["Usage: /split filename size_in_mb"],
            bot.bot_data['bot_loop']
        )
        return
    
     
    size_bytes = int(size_mb) * 1024 * 1024
    if size_bytes <= 0 or size_bytes > 2000*1024*1024:
        await_exec(
            message.reply_text,
            ["size must be greater than 0 and in less than 2000 mb"],
            bot.bot_data['bot_loop']
        )
        return
    
    try:    
        target_path = os.path.join(user.path, name)
        print(target_path)
        if not os.path.exists(target_path) or not os.path.isfile(target_path):
            await_exec(
                message.reply_text,
                ["file not found"],
                bot.bot_data['bot_loop']
            )
            return
    
        i = split_path(target_path, size_bytes)
        await_exec(
            message.reply_text,
            [f"File split into {i} parts."],
            bot.bot_data['bot_loop']
        )
    except Exception as e:
        await_exec(
            message.reply_text,
            [f"Error during splitting: {e}"],
            bot.bot_data['bot_loop']
        )

        
def load_cookie(message:Message, command:str):
    command = command.removeprefix('/load_cookie ')
    user = base.get(message.from_user.id)
    if user.state & ADMIN == 0:
        await_exec(
            message.reply_text,
            ["You are not admin"],
            bot.bot_data['bot_loop']
        )
        return
    path = os.path.join(user.path, command)
    if not os.path.exists(path) or not os.path.isfile(path):
        await_exec(
            message.reply_text,
            ["File not found"],
            bot.bot_data['bot_loop']
        )
        return
    try:
        with open(path, 'r') as f:
            cookies = f.read()
            global YTDLP_COOKIES
            YTDLP_COOKIES = cookies
            
        await_exec(
            message.reply_text,
            ["Cookie loaded successfully"],
            bot.bot_data['bot_loop']
        )
    except Exception as e:
        await_exec(
            message.reply_text,
            [f"Error loading cookie: {e}"],
            bot.bot_data['bot_loop']
        )


def ren(message:Message, command:str):
    command = command.removeprefix('/ren ')
    user = base.get(message.from_user.id)
    command = command.split(",")
    try:
        old = command[0]
        new = command[1]
    except Exception as e: 
        await_exec(
            message.reply_text,
            ["Usage: /ren old_filename,new_filename"],
            bot.bot_data['bot_loop']
        )
        return
    old_path = os.path.join(user.path, old)
    new_path = os.path.join(user.path, new)
    if not os.path.exists(old_path):
        await_exec(
            message.reply_text,
            ["Old file not found"],
            bot.bot_data['bot_loop']
        )
        return
    try:
        os.rename(old_path, new_path)
        await_exec(
            message.reply_text,
            [f"Renamed {old} to {new}"],
            bot.bot_data['bot_loop']
        )
    except Exception as e:
        await_exec(
            message.reply_text,
            [f"Error renaming file: {e}"],
            bot.bot_data['bot_loop']
        )     