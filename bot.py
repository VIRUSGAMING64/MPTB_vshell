from modules import *

def __init__(bot:Application):
    while not bot.running:
        time.sleep(TIMEOUT)
    print(bot.running)
    loop = bot.bot_data.get('bot_loop')
    for admin in ADMINS_ID:
        print(await_exec(bot.bot.send_message,[admin,"bot started..."], target_loop=loop))
        admin_user = base.get(admin)
        if admin_user == None:
            admin_user = newuser(admin)
            base.add(admin_user)
        admin_user.state = ADMIN | LLM
        print(str(admin_user))
    print("=== init end ===")

def __init_web__():
    import web.app

def database_saver():
    while True:
        time.sleep(DB_SAVE_TIMEOUT)
        base.save()

def __pyrodl__():
    while True:
        try:
            dlbot.start()
            break
        except Exception as e:
            print(e)
            
th.Thread(target=__pyrodl__,daemon = True).start()
th.Thread(target=database_saver,daemon = True).start()
th.Thread(target=__init_web__,daemon = True).start()
th.Thread(target=__init__,args=[bot],daemon = True).start()

bot.add_handler(MessageHandler(filters.ALL,on_message))
bot.add_handler(InlineQueryHandler(on_inline_query))

while True:
    try:
        bot.run_polling(allowed_updates=Update.ALL_TYPES)
        break
    except Exception as e:
        print(e)
        time.sleep(10)