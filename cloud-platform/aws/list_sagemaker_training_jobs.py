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

# List all training jobs
response = sagemaker.list_training_jobs()

# Print the list of training jobs
for job in response['TrainingJobSummaries']:
    print(job['TrainingJobName'])
