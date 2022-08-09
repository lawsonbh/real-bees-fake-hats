from fastapi import FastAPI, UploadFile
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI()


@app.post("/upload_bee/")
def upload_bee_photo(file_obj:UploadFile(...), bucket: Optional[str] = None, acl: Optional[str] = None) -> str:
    """
    Upload a bee photo to an S3 bucket
    - **file_obj**: required, a file like object - hopefully it is a nice bee photo
    - **bucket**: the S3 bucket to post the file object to
    - **acl**: the S3 access control list type
    Returns the url of the file you uploaded
    """
    s3_file_link = upload_file(file_obj=file, bucket=bucket, acl=acl)
    return {"message":s3_file_link}

def upload_file(file_obj, bucket: Optional[str] = None, acl: Optional[str] = None) -> str:
    """Upload a file like object to an S3 bucket
    :param file_obj: File like object recognized by FastAPI
    :param bucket: the S3 bucket to post the file object to
    :param acl: the S3 access control list type
    :return: dict containing a value with the URL of the file you uploaded
    """
    s3_bucket = bucket or os.environ["AWS_S3_BUCKET"]

    aws_key = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret = os.environ["AWS_SECRET_ACCESS_KEY"]
    aws_region = os.environ["AWS_REGION"]
    acl = acl or os.environ["AWS_ACL"]

    s3_client = boto3.client('s3',
            aws_access_key_id = aws_key,
            aws_secret_access_key = aws_secret)
    response = s3_client.upload_fileobj(file_obj.file, s3_bucket, file_obj.filename) 

    return response

@app.get("/bees/{file_path:path}")
def fetch_bee_photo(file_path: str):
    return {"file_path": file_path}

@app.delete("/bees/{file_path:path}")
def delete_bee_photo(file_path: str):
    return {"file_path": file_path}


