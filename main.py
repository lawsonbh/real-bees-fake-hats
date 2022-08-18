import os
from typing import Optional

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from sqlmodel import Session

from db import create_db_and_tables, engine
from models import Photo

load_dotenv()

app = FastAPI()


@app.on_event("start_up")
def on_startup():
    create_db_and_tables()


def create_object_s3_url(object_name: str) -> str:
    """Take an object name and construct a url to access it in the s3 bucket
    :param object_name: name of the object in s3
    :return: string representing the url to access the object
    """
    s3_bucket = os.environ["AWS_S3_BUCKET"]
    aws_region = os.environ["AWS_REGION"]

    return f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{object_name}"


def get_bucket_files() -> dict:
    """Take each object in the amazon s3 bucket and map it to a url that
    we can load into the database
    """
    # List of all objects currently in the S3 bucket
    s3_objects = list_objects()

    # Generate a dictionary so we can map each object to a url string
    bee_file_to_url_dict = {
        key: create_object_s3_url(object_name=key) for key in s3_objects
    }

    return bee_file_to_url_dict


def load_bee_photos_into_db():
    """Placeholder function to actually use the sqlmodel session to load instances
    of the Photo class from models.py
    """
    with Session(engine) as session:
        for bee_file, bee_url in get_bucket_files():
            photo = Photo(name=bee_file, url=bee_url)
            session.add(photo)
        session.commit()


@app.post("/upload_bee/")
def upload_bee_photo(
    file_obj: UploadFile, bucket: Optional[str] = None, acl: Optional[str] = None
) -> str:
    """
    Upload a bee photo to an S3 bucket
    - **file_obj**: required, a file like object - hopefully it is a nice bee photo
    - **bucket**: the S3 bucket to post the file object to
    - **acl**: the S3 access control list type
    Returns a dictionary with the url of the file you uploaded as the value of the key
    """
    response = upload_file(file_obj=file_obj, bucket=bucket, acl=acl)
    return {"message": response}


def upload_file(
    file_obj: UploadFile, bucket: Optional[str] = None, acl: Optional[str] = None
) -> str:
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

    s3_client = boto3.client(
        "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
    )

    response = s3_client.upload_fileobj(file_obj.file, s3_bucket, file_obj.filename)

    head = s3_client.head_object(Bucket=s3_bucket, Key=file_obj.filename)
    upload_content_length = head["ContentLength"]

    if upload_content_length == 0:
        raise HTTPException(
            status_code=500, detail="Something went wrong in the file upload process"
        )
    response = f"https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{file_obj.filename}"
    return response


@app.get("/download_bee/", status_code=204)
def download_bee_photo(
    bee_photo_name: str, bucket: Optional[str] = None, acl: Optional[str] = None
) -> str:
    """
    Download a bee photo from an S3 bucket
    - **bee_photo_name**: required, str including file extension
    - **bucket**: the S3 bucket to post the file object to
    - **acl**: the S3 access control list type
    Returns a dictionary with the path of the file you downloaded
    """
    response = download_file(file_name=bee_photo_name, bucket=bucket, acl=acl)
    return {"message": response}


def download_file(
    file_name: str, bucket: Optional[str] = None, acl: Optional[str] = None
) -> str:
    """Upload a file like object to an S3 bucket
    :param file_name: Name of the file to download including its extension
    :param bucket: the S3 bucket to download the file from
    :param acl: the S3 access control list type
    :return: dict containing a value with the path to the file you downloaded
    """
    s3_bucket = bucket or os.environ["AWS_S3_BUCKET"]

    aws_key = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret = os.environ["AWS_SECRET_ACCESS_KEY"]

    s3_client = boto3.client(
        "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
    )
    # TODO: Create parameter in func for changing Key and Filename values

    response = s3_client.download_file(
        Bucket=s3_bucket, Filename=file_name, Key=file_name
    )
    # TODO: Implement an endpoint to list the contents of the bucket
    return response


@app.get("/list_bees/")
def list_bees():
    """List all objects in the S3 bucket. Hopefully its a bunch of bees in hats!
    Returns a dictionary where the value of the message key is the list of object
    names as strings.
    """
    response = list_objects()

    return {"message": response}


def list_objects() -> list:
    """Set up access to the S3 bucket and call the generator to create a list of
    all objects.
    :return: a list of objects from the bucket
    """

    s3_bucket = os.environ["AWS_S3_BUCKET"]

    aws_key = os.environ["AWS_ACCESS_KEY_ID"]
    aws_secret = os.environ["AWS_SECRET_ACCESS_KEY"]

    s3_client = boto3.client(
        "s3", aws_access_key_id=aws_key, aws_secret_access_key=aws_secret
    )

    s3_paginator = s3_client.get_paginator("list_objects_v2")

    all_bees = (
        key
        for key in generate_bucket_keys(paginator=s3_paginator, bucket_name=s3_bucket)
    )

    return all_bees


def generate_bucket_keys(
    paginator,
    bucket_name: str,
    prefix: Optional[str] = "/",
    delimiter: Optional[str] = "/",
    start_after: Optional[str] = "",
):
    """Function to generate and yield all object names from an S3 bucket. Follows
    AWS recommended practice for using paginated results with the list_objects_v2
    utility from boto3.
    :param paginator: a collection from the s3_client
    :param bucket_name: S3 bucket to list the contents of
    :param prefix: S3 limits responses to keys that begin with this character or
    set of characters
    :param delimiter: a character or set of characters that groups objects in S3
    :param start_after: where to start listing from, S3 starts listing after the
    specified key
    :return: generator yielding a string key to the object in the specifed S3
    bucket
    """
    prefix = prefix[1:] if prefix.startswith(delimiter) else prefix
    start_after = (start_after or prefix) if prefix.endswith(delimiter) else start_after
    for page in paginator.paginate(
        Bucket=bucket_name, Prefix=prefix, StartAfter=start_after
    ):
        for content in page.get("Contents", ()):
            yield content["Key"]


@app.delete("/bees/{file_path:path}")
def delete_bee_photo(file_path: str):
    return {"file_path": file_path}
