import re
from tele_bot.bot_init import bot
from functools import partial
from tele_bot.missing_persons_functions.details.ask_identification_mark import ask_identification_mark
import boto3
from api.recognization.recog_new import recognizeFace
from dotenv import dotenv_values
import psycopg2
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from tele_bot.set_logger import logger
from tele_bot.exp_handler.exp_handler import handle_exp

def ask_address(message,img_data_param,name_param,contact_param):
    if(message.content_type == 'text'):
        if re.match(r"^\d+$", message.text): 
            age=message.text
            logger.info("Asking user to enter person's address from ask_address.py line 16")
            bot.send_message(message.chat.id, f"कृपया व्यक्ति का पता दर्ज करें")
            try:
                bot.register_next_step_handler(message,partial( ask_identification_mark,img_data_param=img_data_param,name_param=name_param,contact_param=contact_param,age_param=age))
            except Exception:
                logger.exception("Exception occured in ask_address.py in line 21")
                bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")    
                bot.register_next_step_handler(message,partial(handle_exp)) 
        else:
            logger.info("Asking user to enter correct age of person from ask_address.py line 24")
            bot.send_message(message.chat.id, "अमान्य आयु. कृपया पुन: प्रयास करें.")
            try:
                logger.info("Calling ask_address function from ask_address.py line 27")
                bot.register_next_step_handler(message,partial( ask_address,img_data_param=img_data_param,name_param=name_param,contact_param=contact_param))
            except Exception:
                logger.exception("Exception occured in ask_address.py line 30")
                bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")   
                bot.register_next_step_handler(message,partial(handle_exp)) 

    elif message.content_type =='photo':
        logger.info("processing the image in ask_address.py line 34")
        bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
        file_id=message.photo[-1].file_id
        file=bot.get_file(file_id)
        file_url = file.file_path
        img_data = bot.download_file(file.file_path)
        client=boto3.client('rekognition', region_name='us-east-1')  
        face_detected,res=recognizeFace(client,img_data)

        if face_detected == "Invalid image":
            logger.info("Asking user to enter the image with face from ask_address.py line 47")
            bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

        elif not face_detected:
            logger.info("Asking user for person's name from ask_address.py line 44")
            bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
            def ask_phone_addr(message,img_data_param):
                if(message.content_type == 'text'):    
                    name=message.text
                    logger.info("Asking user for person's number from ask_address.py line 49")
                    bot.send_message(message.chat.id, " कृपया अपने व्यक्ति का फ़ोन नंबर दर्ज करें.")
                    try:
                        def ask_age_addr(message,img_data_param,name_param):
                            if(message.content_type == 'text'):
                                if re.match(r"^\+?\d{10,15}$",message.text):
                                    contact = message.text
                                    logger.info("Asking user for person's age from ask_address.py line 56")
                                    bot.send_message(message.chat.id, f" कृपया व्यक्ति की आयु दर्ज करें.")
                                    try:
                                        logger.info("Calling ask_address.py method from ask_address.py line 59")
                                        bot.register_next_step_handler(message,partial(ask_address,img_data_param=img_data_param,name_param=name_param,contact_param=contact))
                                    except Exception:
                                        logger.exception("Exception occured in ask_address.py line 62")
                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")  
                                        bot.register_next_step_handler(message,partial(handle_exp)) 
                                else:
                                    logger.info("ASking user to enter an alternative person's number from ask-address.py line 65")
                                    bot.send_message(message.chat.id, "अवैध फोन नंबर। कृपया पुन: प्रयास करें।")
                                    try:
                                        logger.info("Calling ask_age_addr function from ask_address.py line 68")
                                        bot.register_next_step_handler(message, ask_age_addr)
                                    except Exception:
                                        logger.exception("Exception occured in ask_address.py line 71")
                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
                                        bot.register_next_step_handler(message,partial(handle_exp)) 
                            elif message.content_type=='photo':
                                logger.info("Processning image from ask_address.py line 74")
                                bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
                                file_id=message.photo[-1].file_id
                                file=bot.get_file(file_id)
                                file_url = file.file_path
                                img_data = bot.download_file(file.file_path)
                                client=boto3.client('rekognition', region_name='us-east-1')  
                                face_detected,res=recognizeFace(client,img_data)  

                                if face_detected == "Invalid image":
                                    logger.info("Asking user to enter the image with face from ask_address.py line 93")
                                    bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

                                elif not face_detected:
                                    logger.info("Asking user for person's name from ask_address.py line 84")
                                    bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
                                    logger.info("Calling ask_phone_addr function from ask_address.py line 86")
                                    bot.register_next_step_handler(message, partial(ask_phone_addr,img_data_param=img_data))
                                    
                                else:
                                    logger.info("Retrieving details from database from ask_address.py line 90")
                                    DB_HOST = dotenv_values('../.env')['DB_HOST']
                                    DB_NAME = dotenv_values('../.env')['DB_NAME']
                                    DB_USER = dotenv_values('../.env')['DB_USER']
                                    DB_PASS = dotenv_values('../.env')['DB_PASS']
                                    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
                                    cursor = conn.cursor()
                                    face_id=res['FaceMatches'][0]['Face']['FaceId']
                                    
                                    select_query = '''SELECT * FROM missing_persons_info WHERE face_id = %s'''
                                    cursor.execute(select_query, (face_id,))
                                    record = cursor.fetchone()

                                    face_id=record[0]
                                    name=record[1]
                                    age=record[2]
                                    address=record[3]
                                    phone=record[4]
                                    image_data=bytes(record[7])
                                    global face_Id
                                    face_Id=face_id
                                    identification_mark=record[8]
                                    
                                    text=f"निम्नलिखित विवरण हैं:\n\nफेस आईडी: {face_id} \nनाम: {name}\nफ़ोन नंबर: {phone}\nआयु: {age}\nपता:{address}\nपहचान के निशान:{identification_mark}\n\n क्या आप इस व्यक्ति को जानते हैं ?"
                                    markup = InlineKeyboardMarkup() # create inline keyboard
                                    markup.add(InlineKeyboardButton("हाँ", callback_data="Yes")) # add edit button
                                    markup.add(InlineKeyboardButton("नहीं", callback_data="No"))# add confirm button
                                    bot.send_photo(message.chat.id,photo=image_data,caption=text, parse_mode="Markdown", reply_markup=markup)
                            else:
                                logger.info("Asking user to enter an image from asK_address.py line 118")
                                bot.send_message(message.chat.id, f" कृपया एक छवि दर्ज करें.")  

                        bot.register_next_step_handler(message, partial(ask_age_addr,img_data_param=img_data_param,name_param=name))

                                
                    except Exception:
                        logger.info("Exception occured in ask_address.py line 125")
                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि") 
                        bot.register_next_step_handler(message,partial(handle_exp)) 

                elif message.content_type=='photo':
                    logger.info("Processing image from ask_address.py line 129")
                    bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
                    file_id=message.photo[-1].file_id
                    file=bot.get_file(file_id)
                    file_url = file.file_path
                    img_data = bot.download_file(file.file_path)
                    client=boto3.client('rekognition', region_name='us-east-1')  
                    face_detected,res=recognizeFace(client,img_data)

                    if face_detected == "Invalid image":
                        logger.info("Asking user to enter the image with face from ask_address.py line 154")
                        bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

                    elif not face_detected:
                        logger.info("Asking user to enter person's name from ask_address.py line 139")
                        bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
                        bot.register_next_step_handler(message, partial(ask_phone_addr,img_data_param=img_data))
                    else:
                        logger.info("Retrieving details from the database from ask_address.py line 143")
                        DB_HOST = dotenv_values('../.env')['DB_HOST']
                        DB_NAME = dotenv_values('../.env')['DB_NAME']
                        DB_USER = dotenv_values('../.env')['DB_USER']
                        DB_PASS = dotenv_values('../.env')['DB_PASS']
                        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
                        cursor = conn.cursor()
                        face_id=res['FaceMatches'][0]['Face']['FaceId']
                        
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

            bot.register_next_step_handler(message, partial(ask_phone_addr,img_data_param=img_data))


        else:
            logger.info("Retrieving details from database from ask_address.py line 175")
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
        logger.info("Asking user to enter a image from ask_address.py line 203")
        bot.send_message(message.chat.id, f" कृपया एक छवि दर्ज करें.")                     

