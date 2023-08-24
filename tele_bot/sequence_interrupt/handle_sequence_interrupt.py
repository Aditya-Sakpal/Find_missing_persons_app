from tele_bot.bot_init import bot
from api.recognization.recog_new import recognizeFace
import boto3
from functools import partial
from dotenv import dotenv_values
import psycopg2
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from tele_bot.missing_persons_functions.details.ask_phone import ask_phone
from tele_bot.exp_handler.exp_handler import handle_exp
from tele_bot.set_logger import logger

def handle_sequence_interrupt(message):
    if message.content_type=='photo':
        bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
        file_id=message.photo[-1].file_id
        file=bot.get_file(file_id)
        file_url = file.file_path
        img_data = bot.download_file(file.file_path)
        client=boto3.client('rekognition', region_name='us-east-1')  
        face_detected,res=recognizeFace(client,img_data)

        if face_detected == "Invalid image":
            logger.info("Asking user to enter the image with face from handle_sequence_interrupt.py line 23")
            bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

        elif not face_detected:
            bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
            bot.register_next_step_handler(message, partial(ask_phone,img_data_param=img_data))
        else:
            DB_HOST = dotenv_values('../.env')['DB_HOST']
            DB_NAME = dotenv_values('../.env')['DB_NAME']
            DB_USER = dotenv_values('../.env')['DB_USER']
            DB_PASS = dotenv_values('../.env')['DB_PASS']
            conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
            cursor = conn.cursor()
            face_id=res['FaceMatches'][0]['Face']['FaceId']
            print(face_id)
            select_query = '''SELECT * FROM missing_persons_info WHERE face_id = %s'''
            cursor.execute(select_query, (face_id,))
            record = cursor.fetchone()
            
            face_id=record[0]
            name=record[1]
            age=record[2]
            address=record[3]
            phone=record[4]
            image_data=bytes(record[7])
            identification_mark=record[8]
            global face_Id
            face_Id=face_id

            text=f"निम्नलिखित विवरण हैं:\n\nफेस आईडी: {face_id} \nनाम: {name}\nफ़ोन नंबर: {phone}\nआयु: {age}\nपता:{address}\nपहचान के निशान:{identification_mark}\n\n क्या आप इस व्यक्ति को जानते हैं ?"
            markup = InlineKeyboardMarkup() # create inline keyboard
            markup.add(InlineKeyboardButton("हाँ", callback_data="Yes")) # add edit button
            markup.add(InlineKeyboardButton("नहीं", callback_data="No"))# add confirm button
            bot.send_photo(message.chat.id,photo=image_data,caption=text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f" कृपया एक छवि दर्ज करें.")    