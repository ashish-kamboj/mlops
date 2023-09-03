## Importing Libraries
import boto3

## AWS Key's
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

## Creating dynamodb resource object
s3 = boto3.resource('s3',
                    region_name='us-east-1',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY

# Specify the S3 bucket name and object key (path)
BUCKET_NAME = "some-bucket-name"
OBJECT_KEY = 'some/file/path/sample.csv'

url = s3_client.generate_presigned_url(
    ClientMethod='get_object',
    Params={'Bucket': BUCKET_NAME, 'Key': OBJECT_KEY},
    ExpiresIn=3600  # URL will expire in 1 hour (3600 seconds)
)

print("Object URL:", url)