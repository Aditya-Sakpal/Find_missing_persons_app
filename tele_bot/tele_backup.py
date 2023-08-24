# from abc import update_abstractmethods
# from update_abstractmethod import update_abstractmethods
import os
import re
from fastapi import Response
import psycopg2
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import dotenv_values
import requests
import boto3
# from telegram.ext import Updater, CallbackQueryHandler,PollAnswerHandler
# from telegram.ext import CallbackQueryHandler, Updater
import time


# print(telegram.__version__)
BOT_TOKEN = dotenv_values('../.env')['api_key']
bot = telebot.TeleBot(BOT_TOKEN)

# updater = Updater(Bo)
# dispatcher = updater.dispatcher

name = None
age = None
contact = None
address = None
image_data=None

face_Id=None

reciever_name=None
reciever_phone=None

# gbl_message=None

def recognizeFace(client,image_data):
    face_matched = False
    res=client.search_faces_by_image(CollectionId="missingpersons",Image={"Bytes":image_data},MaxFaces=1,FaceMatchThreshold=85)
    if (not res['FaceMatches']):
        face_matched = False
    else:
        face_matched = True
        
    return face_matched, res 

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "नमस्ते, मैं एक फॉर्म बॉट हूं। कृपया लापता व्यक्ति की छवि दर्ज करें.")

@bot.message_handler(content_types=['photo'])
def handle_inserted_image(message):
    if message.photo[-1].file_id:
        file_id=message.photo[-1].file_id
        file=bot.get_file(file_id)
        file_url = file.file_path
        img_data = bot.download_file(file.file_path)
        client=boto3.client('rekognition', region_name='us-east-1')  
        face_detected,res=recognizeFace(client,img_data)

        if not face_detected:
            global image_data
            image_data=img_data
            bot.send_message(message.chat.id, f" कृपया व्यक्ति का नाम दर्ज करें.")
            bot.register_next_step_handler(message, ask_phone)
        else:
            DB_HOST = "localhost"
            DB_NAME = "your_new_database"
            DB_USER = "postgres"
            DB_PASS = "password"    
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

            text=f"निम्नलिखित विवरण हैं:\n\nफेस आईडी: {face_id} \nनाम: {name}\nफ़ोन नंबर: {phone}\nआयु: {age}\nपता:{address}\n\n क्या आप इस व्यक्ति को जानते हैं ?"
            markup = InlineKeyboardMarkup() # create inline keyboard
            markup.add(InlineKeyboardButton("हाँ", callback_data="Yes")) # add edit button
            # bot.register_callback_query_handler("Yes",answerCallbackQuery)
            markup.add(InlineKeyboardButton("नहीं", callback_data="No"))# add confirm button
            # bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
            bot.send_photo(message.chat.id,photo=image_data,caption=text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda query: query.data == "Yes")
def answerCallbackQuery(update,context=True ):
   
   
    bot.send_message(update.message.chat.id,"कृपया अपना नाम दर्ज करें")
    bot.register_next_step_handler(update.message,ask_reciever_name)
   

def ask_reciever_name(message):
    global reciever_name
    reciever_name=message.text
    bot.send_message(message.chat.id,"कृपया अपना फोन नंबर दर्ज करें")
    bot.register_next_step_handler(message,ask_reciever_phone)

def ask_reciever_phone(message):
    global reciever_phone
    reciever_phone=message.text
    bot.send_message(message.chat.id,"हमें खुशी है कि आपको अपना प्रियजन मिल गया, हमारी सेवा का उपयोग करने के लिए धन्यवाद")

    DB_HOST = "localhost"
    DB_NAME = "your_new_database"
    DB_USER = "postgres"
    DB_PASS = "password"
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cursor = conn.cursor()
    client = boto3.client('rekognition', region_name='us-east-1') 

    try:
        global reciever_name
        global face_Id
        cursor.execute("UPDATE missing_persons_info SET reciever_name = %s, reciever_contact = %s WHERE face_id = %s", (reciever_name, reciever_phone, face_Id) )   
        print(cursor.rowcount)
        # bot.send_message(message.chat.id," that you found your loved one, thanks for using our service")  
        conn.commit()
        print("Done")
        return Response(status_code=204)
    except Exception:
        print(Exception)



def ask_phone(message):

    global name
    name=message.text

    bot.send_message(message.chat.id, " कृपया अपने व्यक्ति का फ़ोन नंबर दर्ज करें.")
    bot.register_next_step_handler(message, ask_age)

def ask_age(message):
    if re.match(r"^\+?\d{10,15}$",message.text): # check if phone number is valid
        global contact
        contact=message.text
        bot.send_message(message.chat.id, f" कृपया व्यक्ति की आयु दर्ज करें.")
        bot.register_next_step_handler(message, ask_address)
    else:
        bot.send_message(message.chat.id, "अवैध फोन नंबर। कृपया पुन: प्रयास करें।")
        bot.register_next_step_handler(message, ask_age)

def ask_address(message):
    if re.match(r"^\d+$", message.text): # check if age is a number
        global age
        age=message.text
        bot.send_message(message.chat.id, f"कृपया अपना पता दर्ज करें")
        bot.register_next_step_handler(message, enter_details)
        # bot.register_next_step_handler(message,)
    else:
        bot.send_message(message.chat.id, "अमान्य आयु. कृपया पुन: प्रयास करें.")
        bot.register_next_step_handler(message,ask_address)

def enter_details(message):
    DB_HOST = "localhost"
    DB_NAME = "your_new_database"
    DB_USER = "postgres"
    DB_PASS = "password"
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cursor = conn.cursor()
    client = boto3.client('rekognition', region_name='us-east-1') 


    try:
        global name
        global contact
        global address
        global age
        global image_data

        address=message.text
        response = client.index_faces(
            Image={"Bytes": image_data},
            CollectionId='missingpersons',
            DetectionAttributes=['ALL']
        )   
      
        _,new_res=recognizeFace(client,image_data)
        face_id=new_res['FaceMatches'][0]['Face']['FaceId']
       
        cursor.execute("INSERT INTO missing_persons_info (face_id,name, age, address,contact,image) VALUES (%s, %s, %s, %s, %s, %s)", (face_id,name, age, address,contact,image_data))
        conn.commit()
      
        bot.send_message(message.chat.id,"हमने सभी विवरण दर्ज कर लिए हैं, व्यक्ति मिल जाने पर हम आपको सूचित करेंगे")
        return Response(status_code=204)
    except Exception:
        bot.send_message(message.chat.id,"आंतरिक सर्वर त्रुटि उत्पन्न हुई")

bot.polling()
