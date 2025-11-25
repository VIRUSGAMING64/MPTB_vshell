from telegram import *
from modules.gvar import *
from modules.utils import *

def gpt(message:Message):
    user = database.get(message.from_user.id)
    if not (user.state & LLM):
        s = "contact to @VIRUSGAMING64 for access to gpt-5-nano"
        await_exec(message.reply_text,[s])
    if message == None:
        return
    if message.text == None:
        return
    response = model.responses.create(
        model="gpt-5-nano",
        input=message.text,
        
    )    
    res = response.output_text.replace("\\n","\n")
    await_exec(message.reply_text,[res])