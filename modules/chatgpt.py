from telegram import *
from modules.gvar import *

def gpt(message:Message):
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