
from datetime import datetime
import pyrogram.emoji as emojis
from telegram import *
from modules.core.enums import *
import asyncio
from modules.entity import *
import time
from modules.gvar import *


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
    

def GetMedia(message:Message):
    media_type = 0
    if message.video != None:
        media_type += VIDEO
    if message.audio != None:
        media_type += AUDIO
    if message.document != None:
        media_type += DOCUMENT
    if message.photo != ():
        media_type += PHOTO
    if message.voice != None:
        media_type += VOICE
    return media_type


def get_file_id(message: Message):
    typ = GetMedia(message)
    if typ & DOCUMENT:
        return message.document.file_id
    elif typ & AUDIO:
        return message.audio.file_id
    elif typ & VIDEO:
        return message.video.file_id
    elif typ & PHOTO:
        return message.photo[-1].file_id
    elif typ & VOICE:
        return message.voice.file_id
    return None


def t_user2peer(us:User):
    pw = peer()
    pw.bot_premium = 0
    pw.id = us.id
    pw.is_premium = us.is_premium
    if pw.is_premium == None:
        pw.is_premium = 0
    pw.name = us.username
    pw.path = f"env/{pw.name}-{pw.id}"
    pw.state = 0
    return pw


def normal_exec(func,args):
    func(*args)


def await_exec(func,args,loop):
    try:
        if loop == None:
            loop = asyncio.get_running_loop()
    except RuntimeError as e:
        loop = asyncio.new_event_loop()
        print(e)
        
    asyncio.set_event_loop(loop)

    if not isinstance(args, (list, tuple)):
        args = (args,)

    fut = asyncio.run_coroutine_threadsafe(
        func(*args), 
        loop
    )

    while fut.running():
        time.sleep(0.1)
    
    return fut.result()


def getfullpath(args:str):
    return os.path.realpath(args)

def int2path(idx, user):
    try:
        dirs = os.listdir(user.path)
    except OSError:
        return None

    dirs = []
    files = []
    
    for di in dirs:
        full_path = os.path.join(user.path, di)
        if os.path.isdir(full_path):
            dirs.append(di)
        else:
            files.append(di)

    items = dirs + files
    
    if 0 <= idx and idx < len(items):
        return items[idx]
    
    return None


def newuser(id):
    user2 = peer()
    user2.bot_premium = 0
    user2.id = id
    user2.name = "..."
    user2.path = f"env/tmp-{id}"
    user2.is_premium = 0
    user2.state = 0
    try:
        os.mkdir(user2.path)
    except:
        pass 
    return user2


def _parse(user:peer, mess:Message)->peer:
    if user != None and user.id and user.name != "...":
        return user
    
    if user == None:
        user = t_user2peer(mess.from_user)
        base.add(user)
    
    if user.name == "..." and mess.from_user.username:
        user.name = mess.from_user.username
    
    user.path = f"env/{user.name}-{user.id}"
            
    return user



def pyrom(message: Message):
    import pyrogram
    if message is None:
        return None
    
    chat = None
    if message.chat:
        chat_type = str(message.chat.type).upper()
        p_chat_type = None
        if hasattr(pyrogram.enums.ChatType, chat_type):
            p_chat_type = getattr(pyrogram.enums.ChatType, chat_type)
            
        chat = pyrogram.types.Chat(
            id=message.chat.id,
            type=p_chat_type,
            title=message.chat.title,
            username=message.chat.username
        )

    from_user = None
    if message.from_user:
        from_user = pyrogram.types.User(
            id=message.from_user.id,
            is_bot=message.from_user.is_bot,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code
        )

    # Media handling
    photo = None
    if message.photo:
        # PTB returns a list of PhotoSize, we take the last one (biggest)
        p = message.photo[-1]
        photo = pyrogram.types.Photo(
            file_id=p.file_id,
            file_unique_id=p.file_unique_id,
            width=p.width,
            height=p.height,
            file_size=p.file_size,
            date=message.date
        )

    video = None
    if message.video:
        v = message.video
        video = pyrogram.types.Video(
            file_id=v.file_id,
            file_unique_id=v.file_unique_id,
            width=v.width,
            height=v.height,
            duration=v.duration,
            mime_type=v.mime_type,
            file_size=v.file_size,
            file_name=v.file_name,
            date=message.date
        )

    document = None
    if message.document:
        d = message.document
        document = pyrogram.types.Document(
            file_id=d.file_id,
            file_unique_id=d.file_unique_id,
            file_name=d.file_name,
            mime_type=d.mime_type,
            file_size=d.file_size,
            date=message.date
        )
        
    audio = None
    if message.audio:
        a = message.audio
        audio = pyrogram.types.Audio(
            file_id=a.file_id,
            file_unique_id=a.file_unique_id,
            duration=a.duration,
            performer=a.performer,
            title=a.title,
            mime_type=a.mime_type,
            file_size=a.file_size,
            date=message.date
        )

    voice = None
    if message.voice:
        v = message.voice
        voice = pyrogram.types.Voice(
            file_id=v.file_id,
            file_unique_id=v.file_unique_id,
            duration=v.duration,
            mime_type=v.mime_type,
            file_size=v.file_size,
            date=message.date
        )

    return pyrogram.types.Message(
        id=message.id,
        date=message.date,
        chat=chat,
        from_user=from_user,
        text=message.text,
        caption=message.caption,
        photo=photo,
        video=video,
        document=document,
        audio=audio,
        voice=voice,
        media_group_id=message.media_group_id
    )

