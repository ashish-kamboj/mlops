## Importing Libraries
import pickle
import boto3

## Constants
AWS_ACCESS_KEY_ID = '<< >>'
AWS_SECRET_ACCESS_KEY = '<< >>'

S3_BUCKET_NAME='<< >>'
S3_PREFIX = '<< >>'
FILE_NAME = 'sample.pkl'

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

## Read pickle file from s3 bucket
data = pickle.loads(s3_resource.Bucket(S3_BUCKET_NAME).Object(key).get()['Body'].read())
