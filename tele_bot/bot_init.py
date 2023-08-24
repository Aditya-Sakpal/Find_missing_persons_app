import telebot 
from dotenv import dotenv_values
from tele_bot.set_logger import logger

logger.info("bot initialized from bot_init.py")

BOT_TOKEN = dotenv_values('../.env')['api_key']
bot = telebot.TeleBot(BOT_TOKEN)

# bot.polling()