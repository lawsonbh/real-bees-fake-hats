from fastapi import FastAPI
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI()


##TODO: Build out the fast api function placeholder so it is separate from the upload_file function
@app.post("/upload_bee/")
def placeholder():
    response.key = upload_file()
    return {"message":s3_file_link}


def upload_file(filepath: str, bucket: Optional[str] = None, acl: Optional[str] = None) -> str:
    """Upload a file to S3 bucket
    :param filepath: Path to bee photo including filename
    :param bucket: Bucket in s3 to upload to
    :param acl: access control list value for the bucket in s3
    :return: bucketname, path to file in bucket, and file name in bucket  if file uploaded, else False
    """
    s3_bucket = bucket or os.environ["AWS_S3_BUCKET"]

    aws_key = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret = os.environ["AWS_SECRET_ACCESS_KEY"]
    aws_region = os.environ["AWS_REGION"]
    acl = acl or os.environ["AWS_ACL"]

    session = boto3.Session(aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
    s3 = session.resource("s3")
    response = s3.Bucket(s3_bucket).put_object(
            Key=os.path.basename(filepath),Body=open(filepath,"rb"),ACL=acl
            )
    s3_file_link = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{response.key}"
    print(s3_file_link)

    return s3_file_link

@app.get("/bees/{file_path:path}")
def fetch_bee_photo(file_path: str):
    return {"file_path": file_path}

@app.delete("/bees/{file_path:path}")
def delete_bee_photo(file_path: str):
    return {"file_path": file_path}


