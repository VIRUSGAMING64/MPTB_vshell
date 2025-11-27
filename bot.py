from modules import *
def __init__(bot:Application):
    while not bot.running:
        time.sleep(TIMEOUT)
    print(bot.running)
    for admin in ADMINS_ID:
        await_exec(bot.bot.send_message,[admin,"bot started..."])
        admin_user = base.get(admin)
        if admin_user == None:
            admin_user = newuser(admin)
            base.add(admin_user)
        admin_user.state = ADMIN | LLM
        print(str(admin_user))

    import modules.brain

th.Thread(target=__init__,args=[bot]).start()
bot.bot.get_chat
bot.add_handler(MessageHandler(filters.ALL,on_message))
bot.run_polling(allowed_updates=Update.ALL_TYPES)