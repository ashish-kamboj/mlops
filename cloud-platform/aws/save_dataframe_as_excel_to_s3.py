## Importing Libraries
import io
import boto3
import pandas as pd

## Constants
AWS_ACCESS_KEY_ID = 'some_aws_access_key_id'
AWS_SECRET_ACCESS_KEY = 'some_aws_secret_access_key'

S3_BUCKET_NAME='some_s3_bucket_name'
S3_PREFIX = 'some_s3_prefix'
FILE_NAME = 'sample.xlsx'

if(S3_PREFIX is not None or S3_PREFIX.strip() != ''):
    key = S3_PREFIX + '/' + FILE_NAME
else:
    key = FILE_NAME

## Creating dataframe
# initialize data of lists.
data = {'Name': ['Name1', 'Name2', 'Name3', 'Name4'],
        'Age': [20, 21, 19, 18]}
  
# Create DataFrame
df = pd.DataFrame(data)

with io.BytesIO() as output:
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, 'test_sheet')
    data = output.getvalue()


## Creating s3 resource object
s3_resource = boto3.resource(
                's3',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

## Writing dataframe as xlsx to s3
s3_resource.Bucket(S3_BUCKET_NAME).put_object(Key=key, Body=data)


