import logging
import datetime as dt

today = dt.datetime.today()
filename = f"{today.month:02d}-{today.day:02d}-{today.year:02d}.log"

# Set up the logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("TELE_BOT_LOGGER")

file_handler = logging.FileHandler('logs/'+filename)

formatter = logging.Formatter("%(asctime)s:%(levelname)s-%(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)