from fastapi import FastAPI
import boto3
from botocore.exceptions import ClientError
import logging
import os

app = FastAPI()


@app.post("/bees/{file_path:path}")
def store_bee_photo(file_path: str):
    return {"file_path": file_path}

@app.get("/bees/{file_path:path}")
def fetch_bee_photo(file_path: str):
    return {"file_path": file_path}

@app.delete("/bees/{file_path:path}")
def delete_bee_photo(file_path: str):
    return {"file_path": file_path}

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket in s3 to upload to
    :param object_name: S3 object name, default to file_name parameter value
    :return: True if file uploaded, else False
    """

    if object_name is None:
        object_name = os.path.basename(file_name
    
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

