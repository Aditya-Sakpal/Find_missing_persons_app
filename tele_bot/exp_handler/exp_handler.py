from tele_bot.bot_init import bot
from functools import partial

def handle_exp(message):
    bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि") 
    bot.register_next_step_handler(message,partial(handle_exp))
