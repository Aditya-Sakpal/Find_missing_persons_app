from tele_bot.missing_persons_functions.handle_inserted_image import main
from tele_bot.bot_init import bot
from functools import partial
from tele_bot.set_logger import logger
from tele_bot.exp_handler.exp_handler import handle_exp

try:    
    main()
except Exception:
    logger.exception("Exception occured in tele_main.py line 10")
    
    

    bot.polling()