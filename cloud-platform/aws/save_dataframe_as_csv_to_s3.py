## Importing Libraries
from io import StringIO
import pandas as pd
import boto3

## Creating dataframe
# initialize data of lists.
data = {'Name': ['Name1', 'Name2', 'Name3', 'Name4'],
        'Age': [20, 21, 19, 18]}
  
# Create DataFrame
df = pd.DataFrame(data)

## Constants
AWS_ACCESS_KEY_ID = '<< >>'
AWS_SECRET_ACCESS_KEY = '<< >>'

S3_BUCKET_NAME='<< >>'
S3_PREFIX = '<< >>'
FILE_NAME = 'sample.csv'

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

csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)

## Writing dataframe as csv to s3
response = s3_resource.Object(S3_BUCKET_NAME, key).put(Body=csv_buffer.getvalue())
print(response)

