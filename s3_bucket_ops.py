from boto3.s3.transfer import S3UploadFailedError
from botocore.exceptions import ClientError
import boto3
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from io import BytesIO
load_dotenv();
def s3_paginator()->list:
    """
    this function iterates over all pages buckets and return a bucket name list
    """
    
    try:
        s3 = boto3.client("s3");
    except ClientError as e:
        print(f"error trying to instanciate client:")
        print(f"{e.response['Error']['Code']}: {e.response['Error']['Message']}")
    paginator = s3.get_paginator("list_buckets")
    response_iterator = paginator.paginate(
        PaginationConfig={
            "PageSize":50
        }
    )
    bucket_list=[]
    for page in response_iterator:
        if 'Buckets' in page and page["Buckets"]:
            for bucket in page["Buckets"]:
                bucket_list.append(bucket["Name"])
    return bucket_list
    
def s3_upload(bucket_name,file_name):
    """
    this function uploads a file into a bucket
    params:
        bucket_id: string with the bucket id name
        data: string with the pdf data
    returns:
        {message:string }
    """
    try:
        s3 = boto3.resource("s3");
    except ClientError as e:
        print(f"error trying to instanciate client:")
        print(f"{e.response['Error']['Code']}: {e.response['Error']['Message']}")

    bucket=s3.Bucket(bucket_name)
    obj= bucket.Object(os.path.basename(f"ai_reports/{file_name}.pdf"))
    try:
        obj.upload_file(f"ai_reports/{file_name}.pdf")
        return json.dumps({
            "message":"success"
        })
    except S3UploadFailedError as e:
        print(f"error trying to upload file: {e}")

def s3_read_file(bucket_name,file_name):
    """
    this function retrieves a file from a specific bucket
    params:
        bucket_id: string with the bucket id name
        data: string with the pdf data
    """
    try:
        s3 = boto3.client("s3");
    except ClientError as e:
        print(f"error trying to instanciate client:")
        print(f"{e.response['Error']['Code']}: {e.response['Error']['Message']}")
    try:
        response= s3.download_file(
            Bucket=bucket_name,
            Key=f"{file_name}.pdf",
            Filename=f"ai_reports/{file_name}.pdf"
        )    

    except ClientError as e:
        print(f"error trying to instanciate client:")
        print(f"{e.response['Error']['Code']}: {e.response['Error']['Message']}")

    return response


bucket_name='overall-reports'
file_name= "13ac6b59-a9fb-49fd-b699-7c5c620ee57d"
print(s3_upload(bucket_name,file_name))





