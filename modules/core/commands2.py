import requests
import time
from modules.compress.video import VideoCompressor
from modules.core.queues import *
from modules.gvar import *
import os
import psutil
from modules.utils import *
import asyncio
import threading as th
from modules.fuse import *


def stats(message:Message, command:str):
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    m, s = divmod(uptime_seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    uptime_str = f"{int(d)}d-{int(h)}h-{int(m)}m-{int(s)}s"

    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_freq = psutil.cpu_freq()
    cpu_speed = f"{cpu_freq.current:.2f}Mhz" if cpu_freq else "N/A"
    cpu_count = psutil.cpu_count()

    vm = psutil.virtual_memory()

    du = psutil.disk_usage('/')
    
    process = psutil.Process(os.getpid())
    proc_mem = process.memory_info().rss

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

    msg = "📊Estadísticas del Servidor\n\n"
    msg += f"⏳Uptime: {uptime_str}\n"
    msg += f"⚙️CPU: {get_emoji(cpu_percent)} {cpu_percent}\n"
    msg += f"⚡CPU SPEED: {cpu_speed}\n"
    msg += f"💻CPU COUNT: {float(cpu_count)}\n"
    
    msg += f"🤖RAM PROCESS: {get_size(proc_mem)}\n"
    msg += f"🧠RAM: {get_size(vm.total)}\n"
    msg += f"📉RAM USED: {get_emoji(vm.percent)} {vm.percent}\n"
    msg += f"🆓RAM FREE: {get_size(vm.available)}\n"
    
    msg += f"💾TOTAL DISK: {get_size(du.total)}\n"
    msg += f"📀DISK USED: {get_emoji(du.percent)} {du.percent}\n"
    msg += f"🗑DISK FREE: {get_size(du.free)}\n"

    await_exec(
        message.reply_text,
        [msg],
        bot.bot_data['bot_loop']
    )


def comp(message:Message, command:str):
    args = command
    args:str = args.removeprefix("/comp ")


def ren(message:Message, command:str):
    args = command


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
        message.reply_text
        ["video encoded"]
    )