import binascii
from fastapi import Request,APIRouter
from fastapi.params import Form
from fastapi.templating import Jinja2Templates
from handle_data.obj_init import conn,cursor
from handle_data.set_logger import logger

router=APIRouter()

templates=Jinja2Templates(directory="templates")

@router.post("/signin")
async def signin_details(request: Request,number:str=Form(...),password:str=Form(...)):
    try:
        logger.info("Trying to sigin from sigin.py line 15")
        
        logger.info("Creating cursor from sigin.py line 17")
        cursor.execute('''SELECT password FROM users where phone = %s''',(number,))
        logger.info("Query excuted from sigin.py line 15")
        record=cursor.fetchone()[0]
      
        if(record == binascii.hexlify(password.encode()).decode()):
            matched=1
            auth=True
            face_detected=None
            invalid=False
            logger.info("User sigined from sigin.py line 15")
            return templates.TemplateResponse("index.html", {"request":request,"face_detected":face_detected,"auth":auth,"invalid":invalid})
    except Exception:
        logger.info("Invalid Credentials from sigin.py line 15")
        matched=0
        invalid=True
        auth=None
        face_detected=None
        
        return templates.TemplateResponse("index.html", {"request":request,"face_detected":face_detected,"auth":auth,"invalid":invalid})