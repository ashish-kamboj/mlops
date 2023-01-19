## Importing Libraries
import boto3
import pickle

## Data to upload as pickle file
data = #<< Data can be a dataframe, dictionary, text data etc. (In general any data)>>

## Constants
AWS_ACCESS_KEY_ID = '<< >>'
AWS_SECRET_ACCESS_KEY = '<< >>'

S3_BUCKET_NAME='<< >>'
S3_PREFIX = '<< >>'
FILE_NAME = 'pickle_model.pkl'

if(S3_PREFIX is not None or S3_PREFIX.strip() != ''):
    key = S3_PREFIX + '/' + FILE_NAME
else:
    key = FILE_NAME

## Creating s3 client object
s3_client = boto3.client(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

## Creating Pickle object
pickle_byte_obj = pickle.dumps(data)

## Putting file to s3
s3_client.put_object(Body=pickle_byte_obj, Bucket=S3_BUCKET_NAME, Key=key)
