## Importing Libraries
import boto3

## AWS Key's
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

## Define S3 bucket and Prefix
S3_BUCKET_NAME='bucket_name'
S3_PREFIX = 'some_s3_folder_path/file_name'

## Creating s3 resource object
s3_client= boto3.client(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Delete the object from the S3 folder
response = s3_client.delete_object(
    Bucket=S3_BUCKET_NAME,
    Key=S3_PREFIX
)

print(response)