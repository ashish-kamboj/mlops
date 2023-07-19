import boto3
import os

## Function for executing the python script in s3
def lambda_handler(event, context):
    
    # Name of the bucket 
    BUCKET_NAME = 'code_bucket'
    
    # Object to download (File to download from s3)
    OBJECT_NAME = 'python_code/test.py'

    # Filename to save the file to
    FILE_NAME = '/tmp/test.py'
    
    s3_client = boto3.client('s3')
    
    # Downloading python script to tmp directory of Lambda
    if not os.path.isfile(FILE_NAME):
        s3_client.download_file(BUCKET_NAME, OBJECT_NAME, FILE_NAME)
        print('Successfully downloaded the file\n')
    else:
        os.remove(FILE_NAME)
        print("Successfully removed the file from tmp path")
        
        s3_client.download_file(BUCKET_NAME, OBJECT_NAME, FILE_NAME)
        print('Successfully downloaded the file again\n')
    
    # Executing the downloaded python script
    os.system('python ' + FILE_NAME)
    print('\nSuccessfully executed the file')
    