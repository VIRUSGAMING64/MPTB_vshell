from modules.utils.utils2 import *


def GetPathFromMessage(message: Message):
    """
    esta funcion no afecta al funcionamiento si es de la forma:
    @vshell/command id|path
    """
    user = base.get(message.from_user.id)
    comm = message.text.split()
    if len(comm) < 2:
        await_exec(message.reply_text,["Usage: /command <filename> or /command <idx>"], bot.bot_data["bot_loop"])
        return
    
    id = comm[1]
    pth = None
    
    if id.isdigit():
        idx = int(id)
        files = os.listdir(user.path)
        if 0 <= idx < len(files):
            pth = os.path.join(user.path, files[idx])
        else:
            await_exec(message.reply_text,[f"Invalid index: {idx}"], bot.bot_data["bot_loop"])
            return
    else:
        pth = os.path.join(user.path, id)
    
    if not os.path.exists(pth):
        await_exec(message.reply_text,[f"File not found: {id}"], bot.bot_data["bot_loop"])
    return pth

def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    units = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}B"


def split_path(target_path, chunks_sizes):
    i = 0
    with open(target_path, 'rb') as f:
        l = 0
        chunk = ""
        while True:
            if l + 64 * 1024 <= chunks_sizes:
                chunk = f.read(64 * 1024)
                l += 64 * 1024
            else:
                chunk = f.read(chunks_sizes - l)
                l = chunks_sizes

            if not chunk:
                break

            part_filename = f"{target_path}.{str(i + 1).zfill(3)}"
            with open(part_filename, 'ab') as part_file:
                part_file.write(chunk)
            if l == chunks_sizes:
                l = 0
                i+= 1            
            
        i += 1
    return i


def time_formatter(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s") if seconds else "")
    return tmp.strip().strip(",")


def progress(count, total, speed = None, message:Message = None, label = "Downloading"):
    
    print("progress called")
    if datetime.now().second % 2 == 0:
        return  
    
    percentage = count * 100 / total if total > 0 else 0
    
    por = percentage / 10
    color = emojis.RED_CIRCLE
    if por > 4:
        color = emojis.ORANGE_CIRCLE
    if por > 7:
        color = emojis.GREEN_CIRCLE
    
    filled = int(por)
    bar = f"{color}" * filled + f"{emojis.WHITE_CIRCLE}" * (10 - filled)
    
    current = humanbytes(count)
    tot = humanbytes(total)

    speed_text = ""
    eta_text = ""
    if speed:
        try:
            spd_val = float(speed)
            speed_text = f"{humanbytes(spd_val)}/s"
            if spd_val > 0 and total > 0:
                remain = total - count
                eta = remain / spd_val
                eta_text = f" | ⏳ {time_formatter(int(eta))}"
        except (ValueError, TypeError):
            speed_text = f"{speed}/s"

    progtext = f"{label}\n"
    progtext += f"{bar} {percentage:.2f}%\n"
    progtext += f"⚡ {current} / {tot}\n"
    if speed_text:
        progtext += f"🚀 {speed_text}{eta_text}"
    import modules.gvar as gvar
    try:
        await_exec(
            message.edit_text, 
            [progtext], 
            gvar.bot.bot_data['bot_loop']
        )
    except Exception as e:
        print(f"Error updating progress: {e}")
    
    print(progtext)
    return progtext


def parse_user(user:peer, mess:Message)->peer:
    if user != None and user.id and user.name != "...":
        return user
    
    if user == None:
        user = t_user2peer(mess.from_user)
        base.add(user)
    
    if user.name == "..." and mess.from_user.username:
        user.name = mess.from_user.username
    
    user.path = f"env/{user.name}-{user.id}"
    return user

