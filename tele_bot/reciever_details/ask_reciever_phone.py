from tele_bot.bot_init import bot
import psycopg2
import boto3
from dotenv import dotenv_values
from fastapi import Response
from tele_bot.sequence_interrupt.handle_sequence_interrupt import handle_sequence_interrupt
from tele_bot.set_logger import logger
from tele_bot.exp_handler.exp_handler import handle_exp
from functools import partial

def ask_reciever_phone(message,face_Id,reciever_name):
    if(message.content_type == 'text'):
        
        reciever_phone=message.text
        logger.info("Sending a greet message from ask_reciever_phone.py")
        bot.send_message(message.chat.id,"हमें खुशी है कि आपको अपना प्रियजन मिल गया, हमारी सेवा का उपयोग करने के लिए धन्यवाद")

        DB_HOST = dotenv_values('../.env')['DB_HOST']
        DB_NAME = dotenv_values('../.env')['DB_NAME']
        DB_USER = dotenv_values('../.env')['DB_USER']
        DB_PASS = dotenv_values('../.env')['DB_PASS']
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        client = boto3.client('rekognition', region_name='us-east-1') 

        try:
            logger.info("Inserting reciever's details from ask_reciever_phone.py")
            cursor.execute("UPDATE missing_persons_info SET reciever_name = %s, reciever_contact = %s WHERE face_id = %s", (reciever_name, reciever_phone, face_Id) )   
            print(cursor.rowcount)
            conn.commit()
            
            return Response(status_code=204)
        except Exception:
            logger.exception("Exception occured in ask_reciever_phone.py line 32")
            bot.register_next_step_handler(message,partial(handle_exp)) 
            
    else:
        logger.info("handle_sequence_interrupt method called from ask_reciever_phone.py")
        handle_sequence_interrupt(message)