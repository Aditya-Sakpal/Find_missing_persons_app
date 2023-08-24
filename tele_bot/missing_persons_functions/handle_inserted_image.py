from tele_bot.bot_init import bot
import boto3
from api.recognization.recog_new import recognizeFace
import psycopg2
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import dotenv_values
from functools import partial
from tele_bot.missing_persons_functions.details.ask_phone import ask_phone
from tele_bot.reciever_details.ask_reciever_name import ask_reciever_name
from functools import partial
from tele_bot.set_logger import logger
# from tele_bot.exp_handler.exp_handler import handle_exp

face_Id=None
count=0

def main():
    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "नमस्ते, मैं एक फॉर्म बॉट हूं। कृपया लापता व्यक्ति की छवि दर्ज करें.")

    @bot.message_handler(content_types=['photo','document'])
    def handle_inserted_image(message):
        if message.content_type=='photo':
            global count
            count = 0
            bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
            file_id=message.photo[-1].file_id
            file=bot.get_file(file_id)
            file_url = file.file_path
            img_data = bot.download_file(file.file_path)
            client=boto3.client('rekognition', region_name='us-east-1')  
            face_detected,res=recognizeFace(client,img_data)

            if face_detected == "Invalid image":
                logger.info("Asking user to enter the image with face from handle_inserted_image.py line 36")
                bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

            elif not face_detected:
                logger.info("Asking user for the person's name from handle_inserted_image.py line 40")
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
                
                try:
                    logger.info("Retrieving info from the database from handle_inserted_image.py line 48")
                    select_query = '''SELECT * FROM missing_persons_info WHERE face_id = %s'''
                    cursor.execute(select_query, (face_id,))
                    record = cursor.fetchone()
                    print(record)
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
                    markup = InlineKeyboardMarkup() 
                    markup.add(InlineKeyboardButton("हाँ", callback_data="Yes")) 
                    markup.add(InlineKeyboardButton("नहीं", callback_data="No"))
                    bot.send_photo(message.chat.id,photo=image_data,caption=text, parse_mode="Markdown", reply_markup=markup)
                except Exception:
                    logger.exception("Exception occured in handle_inserted_image.py line 70")
                    bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि | कृपया छवि पुनः दर्ज करें")   
                    bot.register_next_step_handler(message,partial(handle_inserted_image))


          

        else:
            logger.info("Asking user to enter the image from handle_inserted_image.py line 82")
            bot.send_message(message.chat.id, f" कृपया एक छवि दर्ज करें.")       
            # return face_id

    @bot.callback_query_handler(func=lambda query: query.data == "Yes")
    def answerCallbackQuery(update,context=True ):
        global face_Id
        logger.info("Asking for the reciever's name from handle_inserted_image.py line 89")
        bot.send_message(update.message.chat.id,"कृपया अपना नाम दर्ज करें")
        try:
            bot.edit_message_reply_markup(update.message.chat.id, update.message.message_id, reply_markup=None)
            bot.register_next_step_handler(update.message,partial(ask_reciever_name,face_Id=face_Id))  
        except Exception:
            logger.exception("Exception occured in handle_inserted_image.py line 91")
            bot.send_message(update.message.chat.id,"आंतरिक सर्वर त्रुटि")
            bot.register_next_step_handler(update.message,partial(handle_server_exp))

    @bot.callback_query_handler(func=lambda query: query.data == "No")
    def answerCallbackQuery1(update,context=True ):
        logger.info("Asking user to enter a different pic from handle_inserted_image.py line 101")
        bot.send_message(update.message.chat.id,"कृपया भिन्न छवि आज़माएँ")
        try:
            bot.edit_message_reply_markup(update.message.chat.id, update.message.message_id, reply_markup=None)
            bot.register_next_step_handler(update.message,partial(handle_inserted_image))      
        except Exception:
            logger.exception("Exception occured in handle_inserted_image.py line 103")
            bot.send_message(update.message.chat.id,"आंतरिक सर्वर त्रुटि")
            bot.register_next_step_handler(update.message,partial(handle_server_exp))
    
    def handle_server_exp(message):
        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
        bot.register_next_step_handler(message,partial(handle_server_exp))



 
    bot.polling(True)   





