## Importing Libraries
import os
import boto3

## Constants
S3_BUCKET_NAME = "bucket_name"
AWS_ACCESS_KEY_ID = 'aws_access_key_id'
AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'

# Set up the S3 client
s3_prod_client = boto3.client('s3', 
                              aws_access_key_id=AWS_ACCESS_KEY_ID, 
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                              )

# Define the local directory containing the files you want to upload
local_directory_base_path = 'some_base_path/'
local_directory_folder = 'some_folder_name/'
local_directory_complete_path = local_directory_base_path + local_directory_folder

# Define the S3 bucket and folder you want to upload the files to
s3_bucket = S3_BUCKET_NAME
s3_folder = 'some_folder_1/some_sub_folder_1'

# Get a list of all files in the local directory
local_files = os.listdir(local_directory_complete_path)

# Loop through each file and upload it to the specified S3 bucket and folder
for file_name in local_files:
    file_path = os.path.join(local_directory_complete_path, file_name)
    s3_object_key = os.path.join(s3_folder, file_name)
    s3_prod_client.upload_file(file_path, s3_bucket, s3_object_key)