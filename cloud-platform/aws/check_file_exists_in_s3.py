## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = '<< >>'
AWS_SECRET_ACCESS_KEY = '<< >>'

S3_BUCKET_NAME='<< >>'
S3_PREFIX = '<< >>'
FILE_NAME = 'sample.txt'

if(S3_PREFIX is not None or S3_PREFIX.strip() != ''):
    key = S3_PREFIX + '/' + FILE_NAME
else:
    key = FILE_NAME

## Creating s3 resource object
s3_resource = boto3.resource(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

## Getting list of files from s3 bucket
bucket = s3_resource.Bucket(S3_BUCKET_NAME)
objs = list(bucket.objects.filter(Prefix=key))
if(len(objs)>0):
    print(f"File is present!")
else:
    print(f"File is not present!")
