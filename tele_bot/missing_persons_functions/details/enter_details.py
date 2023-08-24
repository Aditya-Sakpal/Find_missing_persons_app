import psycopg2
import boto3
from tele_bot.bot_init import bot
from api.recognization.recog_new import recognizeFace
from fastapi import Response
from dotenv import dotenv_values
from functools import partial
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from tele_bot.sequence_interrupt.handle_address_interrupt import ask_address_ent
from tele_bot.set_logger import logger
from tele_bot.exp_handler.exp_handler import handle_exp

def enter_details(message,image_data,name,age,contact,address):
    if(message.content_type == 'text'):
        DB_HOST = dotenv_values('../.env')['DB_HOST']
        DB_NAME = dotenv_values('../.env')['DB_NAME']
        DB_USER = dotenv_values('../.env')['DB_USER']
        DB_PASS = dotenv_values('../.env')['DB_PASS']
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cursor = conn.cursor()
        client = boto3.client('rekognition', region_name='us-east-1') 


        try:
            logger.info("Inserting image into the database from enter_details.py line 25")
            identification_mark=message.text
            response = client.index_faces(
                Image={"Bytes": image_data},
                CollectionId='missingpersons',
                DetectionAttributes=['ALL']
            )   
      
            _,new_res=recognizeFace(client,image_data)
            face_id=new_res['FaceMatches'][0]['Face']['FaceId']
            
            cursor.execute("INSERT INTO missing_persons_info (face_id,name, age, address,contact,image,identification_mark) VALUES (%s, %s, %s, %s, %s, %s, %s)", (face_id,name, age, address,contact,image_data,identification_mark))
            conn.commit()
        
      
            bot.send_message(message.chat.id,"हमने सभी विवरण दर्ज कर लिए हैं, व्यक्ति मिल जाने पर हम आपको सूचित करेंगे")
            return Response(status_code=204)
        except Exception:
            logger.exception("Exception occured in enter_details.py line 43")
            bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि उत्पन्न हुई")
            bot.register_next_step_handler(message,partial(handle_exp)) 

    elif message.content_type =='photo':
        logger.info("Image processing from enter_details.py line 48")
        bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
        file_id=message.photo[-1].file_id
        file=bot.get_file(file_id)
        file_url = file.file_path
        img_data = bot.download_file(file.file_path)
        client=boto3.client('rekognition', region_name='us-east-1')  
        face_detected,res=recognizeFace(client,img_data)      

        if face_detected == "Invalid image":
            logger.info("Asking user to enter the image with face from enter_details.py line 59")
            bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

        elif not face_detected:
            bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")

            def ask_phone_ent(message,img_data_param):
                if(message.content_type == 'text'):
                    name_param=message.text
                    bot.send_message(message.chat.id, " कृपया अपने व्यक्ति का फ़ोन नंबर दर्ज करें.")
                    try:

                        def ask_age_ent(message,img_data_param,name_param):
                            if(message.content_type == 'text'):
                                if re.match(r"^\+?\d{10,15}$",message.text):
                                    contact=message.text
                                    bot.send_message(message.chat.id,f"कृपया व्यक्ति की आयु दर्ज करें")
                                    try:

                                        def ask_address_ent(message,img_data_param,name_param,contact_param):
                                            if(message.content_type=='text'):
                                                if re.match(r"^\d+$", message.text):
                                                    age=message.text
                                                    bot.send_message(message.chat.id, f"कृपया व्यक्ति का पता दर्ज करें")
                                                    try:

                                                        def ask_identification_mark_ent(message,img_data_param,name_param,contact_param,age_param):
                                                            if(message.content_type == 'text'):
                                                                if re.match(r"^[a-zA-Z0-9\s\.,#\-]+$",message.text):
                                                                    address_param=message.text
                                                                    bot.send_message(message.chat.id,"कृपया व्यक्ति का पहचान चिह्न दर्ज करें")
                                                                    try:

                                                                        bot.register_next_step_handler(message,partial(enter_details,image_data=img_data_param,name=name_param,age=age_param,contact=contact_param,address=address_param))

                                                                    except Exception:
                                                                        logger.exception("Exception occured in enter_details.py line 90")
                                                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
                                                                        bot.register_next_step_handler(message,partial(handle_exp)) 
                                                                else:
                                                                    bot.send_message(message.chat.id, "कृपया एक वैध पता दर्ज करें.")
                                                                    try:
                                                                        bot.register_next_step_handler(message,partial(ask_identification_mark_ent,img_data_param=img_data_param,name_param=name_param,contact_param=contact_param))

                                                                    except Exception:
                                                                        logger.exception("Exception occured in enter_details.py line 98")
                                                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")  
                                                                        bot.register_next_step_handler(message,partial(handle_exp)) 

                                                            elif(message.content_type == 'photo'):
                                                                logger.info("Processing image from enter_details.py line 102")
                                                                bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
                                                                file_id=message.photo[-1].file_id
                                                                file=bot.get_file(file_id)
                                                                file_url = file.file_path
                                                                img_data = bot.download_file(file.file_path)
                                                                client=boto3.client('rekognition', region_name='us-east-1')  
                                                                face_detected,res=recognizeFace(client,img_data) 

                                                                if face_detected == "Invalid image":
                                                                    logger.info("Asking user to enter the image with face from enter_details.py line 119")
                                                                    bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

                                                                elif not face_detected:
                                                                    bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
                                                                    bot.register_next_step_handler(message,partial(ask_phone_ent,img_data_param=img_data_param))
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
                                                        bot.register_next_step_handler(message,partial(ask_identification_mark_ent,img_data_param=img_data_param,name_param=name_param,contact_param=contact_param,age_param=age))

                                                    except Exception:
                                                        logger.exception("Exception occured in enter_details.py line 148")
                                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
                                                        bot.register_next_step_handler(message,partial(handle_exp)) 
                                                else:
                                                    bot.send_message(message.chat.id, "अमान्य आयु. कृपया पुन: प्रयास करें.")
                                                    try:
                                                        bot.register_next_step_handler(message,partial( ask_address_ent,img_data_param=img_data_param,name_param=name_param,contact_param=contact_param))
                                                    except Exception:
                                                        logger.exception("Exception occured in enter_details.py line 155")
                                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि") 
                                                        bot.register_next_step_handler(message,partial(handle_exp)) 

                                            elif(message.content_type == 'photo'):
                                                logger.info("Image processing in enter_details.py line 159")
                                                bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
                                                file_id=message.photo[-1].file_id
                                                file=bot.get_file(file_id)
                                                file_url = file.file_path
                                                img_data = bot.download_file(file.file_path)
                                                client=boto3.client('rekognition', region_name='us-east-1')  
                                                face_detected,res=recognizeFace(client,img_data)

                                                if face_detected == "Invalid image":
                                                    logger.info("Asking user to enter the image with face from enter_details.py line 182")
                                                    bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

                                                elif not face_detected:
                                                    bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
                                                    try:
                                                        bot.register_next_step_handler(message,partial(ask_phone_ent,img_data_param=img_data_param))

                                                    except Exception:
                                                        logger.exception("Exception occured in enter_details.py line 174")
                                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
                                                        bot.register_next_step_handler(message,partial(handle_exp)) 
                                                else:
                                                    logger.info("Retrieving details from database from enter_details.py line 177")
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
                                                bot.send_message(message.chat.id, f" कृपया एक छवि दर्ज करें.")  

                                        bot.register_next_step_handler(message,partial(ask_address_ent,img_data_param=img_data_param,name_param=name_param,contact_param=contact))

                                    except Exception:
                                        logger.exception("Exception occured in enter_details.py line 212")
                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
                                        bot.register_next_step_handler(message,partial(handle_exp)) 
                                else:
                                    bot.send_message(message.chat.id, "अवैध फोन नंबर। कृपया पुन: प्रयास करें।")
                                    try:
                                        bot.register_next_step_handler(message,partial(ask_age_ent,img_data_param=img_data_param,name_param=name_param))
                                    except Exception:
                                        logger.exception("Exception occured in enter_details.py line 219")
                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
                                        bot.register_next_step_handler(message,partial(handle_exp)) 

                            elif(message.content_type == 'photo'):
                                logger.info("Image processing in enter_details.py line 222")
                                bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
                                file_id=message.photo[-1].file_id
                                file=bot.get_file(file_id)
                                file_url = file.file_path
                                img_data = bot.download_file(file.file_path)
                                client=boto3.client('rekognition', region_name='us-east-1')  
                                face_detected,res=recognizeFace(client,img_data)

                                if face_detected == "Invalid image":
                                    logger.info("Asking user to enter the image with face from enter_details.py line 253")
                                    bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

                                elif not face_detected:
                                    bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
                                    try:
                                        bot.register_next_step_handler(message, partial(ask_phone_ent,img_data_param=img_data))
                                    except Exception:
                                        logger.exception("Exception occured in enter_details.py line 236")
                                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि")
                                        bot.register_next_step_handler(message,partial(handle_exp)) 
                                else:
                                    logger.info("Retrieving info from the database in enter_details.py line 239")
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
                                    global face_Id
                                    face_Id=face_id
                                    identification_mark=record[8]

                                    xt=f"निम्नलिखित विवरण हैं:\n\nफेस आईडी: {face_id} \nनाम: {name}\nफ़ोन नंबर: {phone}\nआयु: {age}\nपता:{address}\nपहचान के निशान:{identification_mark}\n\n क्या आप इस व्यक्ति को जानते हैं ?"
                                    markup = InlineKeyboardMarkup() # create inline keyboard
                                    markup.add(InlineKeyboardButton("हाँ", callback_data="Yes")) # add edit button
                                    markup.add(InlineKeyboardButton("नहीं", callback_data="No"))# add confirm button
                                    bot.send_photo(message.chat.id,photo=image_data,caption=text, parse_mode="Markdown", reply_markup=markup)

                            else:
                                bot.send_message(message.chat.id, f" कृपया एक छवि दर्ज करें.") 

                        bot.register_next_step_handler(message, partial(ask_age_ent,img_data_param=img_data_param,name_param=name_param))

                    except Exception:
                        logger.exception("Exception occured in enter_details.py line 274")
                        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि") 
                        bot.register_next_step_handler(message,partial(handle_exp))  

                elif(message.content_type == 'photo'):
                    logger.info("Image processing in enter_details.py line 278")
                    bot.send_message(message.chat.id,"कृपया कुछ समय प्रतीक्षा करें")
                    file_id=message.photo[-1].file_id
                    file=bot.get_file(file_id)
                    file_url = file.file_path
                    img_data = bot.download_file(file.file_path)
                    client=boto3.client('rekognition', region_name='us-east-1')  
                    face_detected,res=recognizeFace(client,img_data)

                    if face_detected == "Invalid image":
                        logger.info("Asking user to enter the image with face from enter_details.py line 315")
                        bot.send_message(message.chat.id, f"कृपया एक चेहरा वाली छवि दर्ज करें")   

                    elif not face_detected:
                        bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
                        bot.register_next_step_handler(message, partial(ask_phone_ent,img_data_param=img_data))
                    else:
                        logger.info("Retrieving info from the database in enter_details.py line 291")
                        DB_HOST = dotenv_values('../.env')['DB_HOST']
                        DB_NAME = dotenv_values('../.env')['DB_NAME']
                        DB_USER = dotenv_values('../.env')['DB_USER']
                        DB_PASS = dotenv_values('../.env')['DB_PASS']
                        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
                        cursor = conn.cursor()
                        face_id=res['FaceMatches'][0]['Face']['FaceId']
                        logger.info("Retrieving info from the database from ask_phone.py line 45")
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

            bot.register_next_step_handler(message, partial(ask_phone_ent,img_data_param=img_data))

        else:
            logger.info("Retrieving info from the database in enter_details.py line 325")
            DB_HOST = dotenv_values('../.env')['DB_HOST']
            DB_NAME = dotenv_values('../.env')['DB_NAME']
            DB_USER = dotenv_values('../.env')['DB_USER']
            DB_PASS = dotenv_values('../.env')['DB_PASS']
            conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
            cursor = conn.cursor()
            face_id=res['FaceMatches'][0]['Face']['FaceId']

            try:
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
                logger.exception("Exception occured in enter_details.py line 356")
                bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि | कृपया छवि पुनः दर्ज करें")   
                bot.register_next_step_handler(message,partial(handle_exp)) 
                    
    else:
        logger.info("Asking user to enter an image from enter_details.py line 360")
        bot.send_message(message.chat.id, f" कृपया एक छवि दर्ज करें.")                     

    