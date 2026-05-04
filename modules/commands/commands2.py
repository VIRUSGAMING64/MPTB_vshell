from modules.commands.commands3 import *

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
    for child in process.children(recursive=True):
        try:
            proc_mem += child.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
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
    args = GetPathFromMessage(message)
    if args == None:
        return
    
    output_file = f"{args}.tar"

    try:
        await_exec(
            message.reply_text, 
            ["Compressing..."],
            bot.bot_data['bot_loop']
        )
        tar = Tar(output_file)
        tar.add(args)
        tar.close()
        await_exec(message.reply_text, ["Compressed successfully!"], bot.bot_data['bot_loop'])
    except Exception as e:
        await_exec(message.reply_text, [f"Error: {e}"], bot.bot_data['bot_loop'])

def x265(message:Message, command:str):
    filename = GetPathFromMessage(message)
    if filename == None:
        return
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
    path = GetPathFromMessage(message)
    user = base.get(message.from_user.id)
    
    if path == "..":
        user.path = os.path.dirname(user.path)
        if len(user.path) <= 4:
            user.path = f"env/{user.name}-{user.id}"
    else:
        user.path +=f"/{path}"

    print(user.path,path)#! usar os.path.join
    base.add(user)    
    await_exec(message.reply_text, [f"directory changed to {user.path}"], bot.bot_data['bot_loop'])
