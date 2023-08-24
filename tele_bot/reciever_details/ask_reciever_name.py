from tele_bot.bot_init import bot
from functools import partial
from tele_bot.reciever_details.ask_reciever_phone import ask_reciever_phone
from dotenv import dotenv_values
from tele_bot.sequence_interrupt.handle_sequence_interrupt import handle_sequence_interrupt
from tele_bot.set_logger import logger

def ask_reciever_name(message,face_Id):
    if(message.content_type == 'text'):
        logger.info("Asking for user phone number from ask_reciver_name.py")
        reciever_name=message.text
        bot.send_message(message.chat.id,"कृपया अपना फोन नंबर दर्ज करें")
        bot.register_next_step_handler(message,partial(ask_reciever_phone,face_Id=face_Id,reciever_name=reciever_name))
    else:
        logger.info("handle_sequence_interrupt method called from ask_reciver_name.py")
        handle_sequence_interrupt(message)
        

