## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = '<< >>'
AWS_SECRET_ACCESS_KEY = '<< >>'

S3_BUCKET_NAME='bucket_name'
S3_PREFIX = 'some/s3/folder/path'
LOCAL_FILE_PATH = '/some/path/sample.txt'
OUTPUT_FILE_NAME = 'sample.txt'

if(S3_PREFIX is not None or S3_PREFIX.strip() != ''):
    key = f"{S3_PREFIX}/{OUTPUT_FILE_NAME}"
else:
    key = OUTPUT_FILE_NAME

## Creating s3 resource object
s3_resource = boto3.resource(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

## Uploading file to s3
bucket = s3_resource.Bucket(S3_BUCKET_NAME)
bucket.upload_file(LOCAL_FILE_PATH, key)
