## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1'

## Set up the Amazon SageMaker client
sagemaker = boto3.client('sagemaker',
                          region_name=region_name, 
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

## Define the name of the notebook instance to start
notebook_instance_name = 'notebook-instance-name'

## Describe the notebook instance
response = sagemaker.describe_notebook_instance(
    NotebookInstanceName=notebook_instance_name
)

# Print the response
print(response)