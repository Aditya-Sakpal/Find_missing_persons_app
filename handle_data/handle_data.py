import base64
from fastapi.templating import Jinja2Templates
from dotenv import dotenv_values
from fastapi import APIRouter, Request, File, UploadFile,Form,Response
from typing import List
from api.recognization.recog_new import recognizeFace
from starlette.staticfiles import StaticFiles
import os
from handle_data.obj_init import conn,client,cursor
from handle_data.set_logger import logger

templates=Jinja2Templates(directory="templates")
os.environ['AWS_ACCESS_KEY_ID'] = dotenv_values('.env')['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY'] =dotenv_values('.env')['AWS_SECRET_ACCESS_KEY']

router=APIRouter()

router.mount("/static", StaticFiles(directory="static"), name="static")

@router.post("/submit")
async def submit_details(request: Request,file: List[UploadFile] = File(...)):
    logger.info('Image inserted , in handle_data.py line 24')
    image_data = await file[0].read()  

    logger.info('Sending the image for detection , in handle_data.py line 27')
    face_detected,res=recognizeFace(client,image_data)

    if face_detected == "Invalid image":
        logger.info('Image is invalid , in handle_data.py line 31')
        auth=True
        return templates.TemplateResponse("index.html", {"request":request,"face_detected": face_detected,"auth":auth})             

    elif not face_detected :
        logger.info('Face is not detected, in handle_data.py line 36')
        
       
        auth=True
        return templates.TemplateResponse("index.html", {"request":request,"face_detected": face_detected,"auth":auth})
    else:
        logger.info('Face is detected , in handle_data.py line 42')
        try:
            
            logger.info('Creating the cursor , in handle_data.py line 42')
            face_id=res['FaceMatches'][0]['Face']['FaceId']
           
            select_query = '''SELECT * FROM missing_persons_info WHERE face_id = %s'''
            cursor.execute(select_query, (face_id,))
            record = cursor.fetchone()

            
               
            if record:
                logger.info('Record found in database , in handle_data.py line 54')

                columns = ['face_id', 'name', 'age', 'address', 'contact_info','reciever_name','reciever_phone','image','identification_mark']
                record_dict = dict(zip(columns, record))
                record_dict['image']=base64.b64encode(record_dict['image']).decode('utf-8')
                confidence=res['FaceMatches'][0]['Face']['Confidence']
                auth=True
                
                return templates.TemplateResponse("index.html",{"request":request,"face_detected":face_detected,"auth":auth,"record_dict": record_dict,"confidence":confidence,"face_id":face_id})
            else:
                logger.info('Record not found in the database , in handle_data.py line 64')
                auth=True
                face_detected=False
                return templates.TemplateResponse("index.html",{"request":request,"face_detected":face_detected,"auth":auth})
        except Exception:
            logger.info('Exception occured in handle_data.py line 69')
            return templates.TemplateResponse("index.html", {"request":request,"face_detected": face_detected,"auth":auth})


@router.post("/insertdata")
async def submit_details(name: str = Form(...), age: int = Form(...), address: str = Form(...),contact: str =Form(...),identification_mark: str =Form(...),file: List[UploadFile] = File(...)):
    logger.info('Called /insertdata in handle_data.py line 75')
    
    
    img_data=await file[0].read()  

    try:
        logger.info('Image inserting into the collection, in handle_data.py line 81')
        response = client.index_faces(
            Image={"Bytes": img_data},
            CollectionId='missingpersons',
            DetectionAttributes=['ALL']
        )  
        logger.info('Image inserted into the collection , in handle_data.py line 87')
        face_id=response['FaceRecords'][0]['Face']['FaceId']
        cursor.execute("INSERT INTO missing_persons_info (face_id,name, age, address,contact,image,identification_mark) VALUES (%s, %s, %s, %s, %s, %s, %s)", (face_id,name, age, address,contact,img_data,identification_mark))
        logger.info('Data inserted into the database, in handle_data.py line 90')
        conn.commit()
        return Response(status_code=204)
    except Exception as e:
        logger.info('Exception occured, in handle_data.py line 94')
        return {"message": "Error occurred during form submission", "error": str(e)}





@router.post("/insertrecieverdata")
async def submit_reciever_details(name: str = Form(...),contact: str = Form(...),face_id: str = Form(...)):
    logger.info('Called /insertrecieverdata , in handle_data.py line 106')
    cursor = conn.cursor()


    try:

        cursor.execute("UPDATE missing_persons_info SET reciever_name = %s, reciever_contact = %s WHERE face_id = %s", (name, contact, face_id))
        logger.info('Recievers data inserted in handle_data.py line 113')
        conn.commit()
        
        return Response(status_code=204)
    except Exception as e:
        logger.info('Exception occured , in handle_data.py line 118')
        return {"message": "Error occurred during form submission", "error": str(e)}
  
        


