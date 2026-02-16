from modules.core.commands.commands3 import *


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_emoji(percent):
    if percent < 60:
        return "🟢"
    elif percent < 85:
        return "🟡"
    else:
        return "🔴"

def stats(message:Message, command:str):
    boot_time       = psutil.boot_time()
    uptime_seconds  = time.time() - boot_time
    m, s            = divmod(uptime_seconds, 60)
    h, m            = divmod(m, 60)
    d, h            = divmod(h, 24)
    uptime_str      = f"{int(d)}d-{int(h)}h-{int(m)}m-{int(s)}s"
    cpu_percent     = psutil.cpu_percent(interval=0.1)
    cpu_freq        = psutil.cpu_freq()
    cpu_speed       = f"{cpu_freq.current:.2f}Mhz" if cpu_freq else "N/A"
    cpu_count       = psutil.cpu_count()
    vm              = psutil.virtual_memory()
    du              = psutil.disk_usage('/')
    process         = psutil.Process(os.getpid())
    proc_mem        = process.memory_info().rss
    msg             =  f"📊Estadísticas del Servidor\n\n"
    msg             += f"⏳Uptime: {uptime_str}\n"
    msg             += f"⚙️CPU: {get_emoji(cpu_percent)} {cpu_percent}\n"
    msg             += f"⚡CPU SPEED: {cpu_speed}\n"
    msg             += f"💻CPU COUNT: {float(cpu_count)}\n"
    msg             += f"🤖RAM PROCESS: {get_size(proc_mem)}\n"
    msg             += f"🧠RAM: {get_size(vm.total)}\n"
    msg             += f"📉RAM USED: {get_emoji(vm.percent)} {vm.percent}\n"
    msg             += f"🆓RAM FREE: {get_size(vm.available)}\n"
    msg             += f"💾TOTAL DISK: {get_size(du.total)}\n"
    msg             += f"📀DISK USED: {get_emoji(du.percent)} {du.percent}\n"
    msg             += f"🗑DISK FREE: {get_size(du.free)}\n"

    await_exec(
        message.reply_text,
        [msg],
        bot.bot_data['bot_loop']
    )


def comp(message:Message, command:str):
    args = command.removeprefix("/comp ").strip()

    user = base.get(message.from_user.id)
    target_path = None

    if args.isnumeric():
        try:
            target_path = int2path(int(args), user)
            if target_path:
                target_path = os.path.join(user.path, target_path)
            else:
                await_exec(
                    message.reply_text, 
                    ["Index not found"], 
                    bot.bot_data['bot_loop']
                )
                return
        except Exception:
            await_exec(
                message.reply_text, 
                ["File not found by index"], 
                bot.bot_data['bot_loop']
            )
            return
    else:
        target_path = os.path.join(user.path, args)
    
    if not os.path.exists(target_path):
        await_exec(
            message.reply_text, 
            ["File not found"], 
            bot.bot_data['bot_loop']
        )
        return
    
    output_file = f"{target_path}.tar"

    try:
        await_exec(
            message.reply_text, 
            ["Compressing..."],
            bot.bot_data['bot_loop']
        )
        tar = Tar(output_file)
        tar.add(target_path)
        tar.close()
        await_exec(message.reply_text, ["Compressed successfully!"], bot.bot_data['bot_loop'])
    except Exception as e:
        await_exec(message.reply_text, [f"Error: {e}"], bot.bot_data['bot_loop'])

def x265(message:Message, command:str):
    filename = command.removeprefix('/x265 ')
    message = await_exec(message.reply_text,["encoding..."])
    compressor = VideoCompressor(callback=progress,args=[None,message,"encoding..."])
    if not compressor.set_file(filename):
        await_exec(
            message.reply_text,
            ["File not found..."]
        )
        return
    
    if not compressor.compress():
        await_exec(
            message.reply_text,
            ["Error compressing..."]
        )
        return
    
    await_exec(
        message.reply_text,
        ["video encoded"],
        bot.bot_data['bot_loop']
    )


def queues(message:Message,command:str):
    user = base.get(message.from_user.id)
    if not user.id in ADMINS_ID:
        await_exec(message.reply_text,["access denied [not admin]"], bot.bot_data['bot_loop'])
        return
    mes = f"""running actions: {runner.running}\n"""
    mes+= f"Messages: {len(actions.messages)}\n"
    mes+= f"Urls: {len(actions.url)}\n"
    mes+= f"Donwload media: {actions.download_media}\n"
    mes+= f"Upload: {actions.upload_media}\n"    
    await_exec(
        message.reply_text,
        [mes], 
        bot.bot_data['bot_loop']
    )
    

def upload(message:Message,command:str):
    command = command.removeprefix("/upload ")
    await_exec(message.reply_text, ["upload pushed to queue"],
        bot.bot_data['bot_loop'])
    actions.upload_media.append(message)


def cd(message:Message,command:str):
    path = command.removeprefix("/cd ").strip()
    user = base.get(message.from_user.id)
    print(path)
    try:
        if path.isnumeric():
            path = int2path(int(path),user)
            if path == None:
                await_exec(message.reply_text, ["index not found"], bot.bot_data['bot_loop'])
                return
            
    except Exception as e:
        await_exec(message.reply_text, [f"error changing dir {str(e)}"], bot.bot_data['bot_loop'])
        return
    
    if not (os.path.exists(user.path+"/"+path) or not  os.path.isdir(user.path+"/"+path)) and path != "..":
        await_exec(message.reply_text, ["path not found or not a directory"], bot.bot_data['bot_loop'])
        return
    
    if path == "..":
        user.path = os.path.dirname(user.path)
        if len(user.path) <= 4:
            user.path = f"env/{user.name}-{user.id}"
    else:
        user.path +=f"/{path}"

    print(user.path,path)
    base.add(user)    
    await_exec(message.reply_text, [f"directory changed to {user.path}"], bot.bot_data['bot_loop'])