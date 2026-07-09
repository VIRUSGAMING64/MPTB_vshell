from telegram import *
from telegram.ext import *
from modules.core.queues import *
from modules.gvar import *


# On message actions {#131 }
async def on_message(update:Update,context):
    print(f"message recived [...]")
    message = update.message
    if message.chat.type == Chat.PRIVATE:
        direct_message(update.message)
    elif message.chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        group_message(message)
    elif message.chat.type == Chat.CHANNEL:
        channel_message(message)
    else:
        unknow_message(message)

async def on_inline_query(update:Update,context):
    query = update.inline_query
    print(query)
    await_exec(
        query.answer,
        [[
            InlineQueryResultArticle(
                id=str(time.time_ns()),
                title="Not implemented",
                input_message_content=InputTextMessageContent(
                    "Inline mode is not implemented yet."
                )
            )
        ]]
    )

def direct_message(message:Message):
    print(message.from_user.name+" sent a message")
    actions.push(message)

def group_message(message:Message):
    print(message.text,BOT_HANDLER)
    if message.text.startswith(BOT_HANDLER + " "):
        print("group message for bot detected")
        actions.push(message)
    elif message.reply_to_message != None:
        print("group message for bot detected")
        if message.reply_to_message.from_user.id == int(BOT_ID):
            actions.push(message)

def channel_message(message:Message):
    pass

def unknow_message(message:Message):
    pass