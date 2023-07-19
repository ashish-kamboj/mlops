## Importing Libraries
import pandas as pd
import boto3

## Constants
AWS_ACCESS_KEY_ID = '<< >>'
AWS_SECRET_ACCESS_KEY = '<< >>'

S3_BUCKET_NAME='<< >>'
S3_PREFIX = '<< >>'
FILE_NAME = 'sample.xlsx'

if(S3_PREFIX is not None or S3_PREFIX.strip() != ''):
    key = S3_PREFIX + '/' + FILE_NAME
else:
    key = FILE_NAME

## Creating s3 resource object
s3_client = boto3.client(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

## Reading file from s3 as object
obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
data = obj['Body'].read()
df = pd.read_excel(data)
