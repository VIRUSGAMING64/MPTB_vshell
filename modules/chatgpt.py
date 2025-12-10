from telegram import *
from modules.gvar import *
from modules.utils import *

def gpt(message:Message):
    try:
        user = base.get(message.from_user.id)

        print(str(user))
        if not (user.state & LLM):
            s = "contact to any admin for access to gpt-5-nano"
            await_exec(message.reply_text,[s])
            return
        
        if message == None:
            return
        
        if message.text == None:
            return
        
        response = model.responses.create(
            model="gpt-5-nano",
            input=message.text,
            max_output_tokens=10000,           
        )    
        res = response.output_text.replace("\\n","\n")
        await_exec(message.reply_text,[res])
    except Exception as e:
        await_exec(message.reply_text,[f"error {str(e)}"])