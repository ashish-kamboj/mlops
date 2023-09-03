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

# Specify the S3 bucket name and prefix (path)
BUCKET_NAME = "some-bucket-name"
PREFIX = 'some/folder/name'

# Initialize a set to store unique subfolder names
unique_subfolders = set()

# List common prefixes (subfolders) in the specified bucket and prefix
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX, Delimiter='/')
print(response)

# Extract and print unique subfolder names
if 'CommonPrefixes' in response:
    for common_prefix in response['CommonPrefixes']:
        subfolder = common_prefix['Prefix'].split('/')[0]  # Assuming subfolder is at index 1
        unique_subfolders.add(subfolder)

print(unique_subfolders)
# Print the unique subfolder names
for subfolder in unique_subfolders:
    print(subfolder)