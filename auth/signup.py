from fastapi import Request,APIRouter
from fastapi.params import Form
from fastapi.templating import Jinja2Templates
from handle_data.obj_init import conn,cursor
import binascii
from handle_data.set_logger import logger
import re



# app=FastAPI()
router=APIRouter()
templates=Jinja2Templates(directory="templates")

@router.post("/signup")
async def signup_details(request: Request,name: str = Form(...),number: str = Form(...),password:str = Form(...)):
    logger.info("Trying to signup from signup.py line 17")
    if re.match(r"^\+?\d{10,15}$",number) and re.match(r'^.{7,}$',password):
        logger.info("Valid credentails entered from signup.py line 19")
        
   
        logger.info("Cursor created from signup.py line 22")
        password=binascii.hexlify(password.encode()).decode()
    
        cursor.execute("INSERT INTO users (name,phone,password) VALUES (%s, %s, %s)", (name, number,password))
        logger.info("Query executed from signup.py line 26")
        conn.commit()
       
        auth=True
        invalid=False
        face_detected=None
        return templates.TemplateResponse("index.html", {"request":request,"face_detected":face_detected,"auth":auth,"invalid":invalid})
    else:
        logger.info("Invalid credentials entered from signup.py line 35")
        invalid=True
        auth=None
        face_detected=None
        return templates.TemplateResponse("index.html", {"request":request,"face_detected":face_detected,"auth":auth,"invalid":invalid})

