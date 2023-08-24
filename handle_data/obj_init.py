import boto3
from dotenv import dotenv_values
import psycopg2

client = boto3.client('rekognition', region_name='us-east-1')


DB_NAME=dotenv_values('.env')['DB_NAME']
DB_USER=dotenv_values('.env')['DB_USER']
DB_PASS=dotenv_values('.env')['DB_PASS']
DB_HOST=dotenv_values('.env')['DB_HOST']
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cursor = conn.cursor()