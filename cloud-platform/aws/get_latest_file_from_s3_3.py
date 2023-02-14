## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = '<< >>'
AWS_SECRET_ACCESS_KEY = '<< >>'

S3_BUCKET_NAME='bucket_name'
S3_PREFIX = 'some/s3/folder/path'

## Creating s3 resource object
s3_client= boto3.client(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

## Getting latest file from s3 bucket
def get_most_recent_s3_object(s3_client, bucket_name, prefix, file_pattern):
    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    latest = None
    for page in page_iterator:
        if "Contents" in page:
            page_filtered_objects = [obj for obj in page['Contents'] if file_pattern in obj['Key']]
            latest2 = max(page_filtered_objects, key=lambda x: x['LastModified'])
            if latest is None or latest2['LastModified'] > latest['LastModified']:
                latest = latest2
    return latest

latest_file = get_most_recent_s3_object(s3_client, S3_BUCKET_NAME, S3_PREFIX, file_pattern="some-file-pattern")

## Print latest(or recent) file which is a combination of 'prefix/objectname'
print(latest_file['Key'])