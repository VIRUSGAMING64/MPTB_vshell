import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError as e:
    print(e)
    asyncio.set_event_loop(asyncio.new_event_loop())
from dotenv import load_dotenv
load_dotenv()
from modules.fuse.file import *
from pyrogram import *
import os
API_ID=os.getenv("API_ID")
API_HASH=os.getenv("API_HASH")
TOKEN = os.getenv("TOKEN")

bot = Client(
    "fuse_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)

bot.start()

f=file(bot,1659735368)
f.max_size = 4
f.write(b"hello world")
f.name = "candela"
f.created_at = datetime.datetime.now().isoformat()
f.close()