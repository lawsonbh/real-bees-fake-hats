from fastapi import FastAPI, File, UploadFile
import boto3
from botocore.exceptions import ClientError
import logging
import os

app = FastAPI()


@app.post("/upload_bee/")
def upload_file(file: UploadFile, bucket: str):
    """Upload a file to S3 bucket
    :param file: FastAPI type for UploadFile
    :param bucket: Bucket in s3 to upload to
    :return: bucketname, path to file in bucket, and file name in bucket  if file uploaded, else False
    """
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file.file, bucket)
    except ClientError as e:
        logging.error(e)
        return False
    return {"message":bucket+file.filename}

@app.get("/bees/{file_path:path}")
def fetch_bee_photo(file_path: str):
    return {"file_path": file_path}

@app.delete("/bees/{file_path:path}")
def delete_bee_photo(file_path: str):
    return {"file_path": file_path}


