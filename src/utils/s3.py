import boto3
import os
import io

from PIL import Image
from io import BytesIO

from urllib.request import Request, urlopen
from botocore.config import Config


config = Config(
    client_context_params={
        'use_accelerate_endpoint': False
    }
)

BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_READ_URL = os.getenv('AWS_S3_READ_URL')
REGION_NAME = os.getenv('AWS_REGION_NAME')
ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

session = boto3.session.Session()
client = session.client('s3',
                        config=config,
                        region_name=REGION_NAME,
                        endpoint_url=ENDPOINT_URL,
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def pull_file_from_s3(url):
    try:
        response = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        image = Image.open(BytesIO(urlopen(response).read()))
        return image

    except:
        return None

def push_image_to_s3(image, file_name):
    
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format="JPEG")
    in_mem_file.seek(0)
    
    client.upload_fileobj(in_mem_file, BUCKET_NAME, file_name , ExtraArgs={'ContentType': 'image/jpeg', "ACL": 'public-read'})
    
    result_url = f"https://{BUCKET_NAME}.{AWS_READ_URL}/{file_name}"
    return result_url

# test
if __name__=="__main__":
    
    # send
    image = Image.open("test.jpeg")
    s3_url = push_image_to_s3(image, "test.jpeg")
    print(s3_url)
    
    # receive
    # url = "xxx"
    # image = pull_file_from_s3(url)
    # image.save("result.jpeg")
