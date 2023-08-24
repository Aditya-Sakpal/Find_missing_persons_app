
import boto3
from dotenv import dotenv_values



def delete_faces_from_collection(collection_id, faces):

    session = boto3.Session(
        aws_access_key_id=dotenv_values('.env')['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=dotenv_values('.env')['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    client = session.client('rekognition')
    response = client.delete_faces(CollectionId=collection_id,
                                   FaceIds=faces)

    print(str(len(response['DeletedFaces'])) + ' faces deleted:')
    for faceId in response['DeletedFaces']:
        print(faceId)
    return len(response['DeletedFaces'])


def main():
    collection_id = 'missingpersons'
    faces = []
    faces.append("cea2d95d-0444-4e82-a38e-f4d46757099a")

    faces_count = delete_faces_from_collection(collection_id, faces)
    print("deleted faces count: " + str(faces_count))

if __name__ == "__main__":
    main()
