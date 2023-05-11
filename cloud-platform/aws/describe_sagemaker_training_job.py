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

## Define the name of the training job to describe
training_job_name = 'XGBoost-tuner-08-001-00000000'

## Describe the training job
response = sagemaker.describe_training_job(
    TrainingJobName=training_job_name
)

## Print the response
print(response)
