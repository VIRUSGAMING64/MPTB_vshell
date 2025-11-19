from modules import *
def __init__(bot:Application):
    while not bot.running:
        time.sleep(TIMEOUT)
    print(bot.running)
    import modules.brain

th.Thread(target=__init__,args=[bot]).start()

bot.add_handler(MessageHandler(filters.ALL,on_message))
bot.run_polling(allowed_updates=Update.ALL_TYPES)