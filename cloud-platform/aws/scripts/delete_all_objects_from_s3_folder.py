## Importing Libraries
import boto3

## AWS Key's
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

## Define S3 bucket and Prefix
S3_BUCKET_NAME='bucket_name'
S3_PREFIX = 'some_s3_folder_path/'

## Creating s3 resource object
s3_client= boto3.client(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# List all objects in the s3 folder
objects = s3_client.list_objects(Bucket=S3_BUCKET_NAME, Prefix=S3_PREFIX)['Contents']

# Delete all objects in the s3 folder
for obj in objects:
    response = s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=obj['Key'])
    print(response)