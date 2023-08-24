import boto3
from dotenv import dotenv_values

session = boto3.Session(
    aws_access_key_id=dotenv_values('.env')['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=dotenv_values('.env')['AWS_SECRET_ACCESS_KEY'],
    region_name='us-east-1'
)


s3 = session.client('s3')

def recognizeFace(client,image_data):
    try:
        face_matched = False
        
        res=client.search_faces_by_image(CollectionId='missingpersons',Image={"Bytes":image_data},MaxFaces=1,FaceMatchThreshold=85)
        if (not res['FaceMatches']):
            face_matched = False
        else:
            face_matched = True
            
        return face_matched, res 
    except Exception:
        face_matched="Invalid image"
        res=None
        return face_matched,res