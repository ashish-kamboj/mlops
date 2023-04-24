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

## Define the parameters for the notebook instance
notebook_instance_name = 'notebook-instance-name'
instance_type = 'ml.t2.medium'
role_arn = 'arn:aws:iam::123456789012:role/service-role/AmazonSageMaker-ExecutionRole-20190101T000001'
subnet_id = 'subnet-0123456789abcdef'
security_group_ids = ['sg-0123456789abcdef']

# Create the notebook instance
response = sagemaker.create_notebook_instance(
    NotebookInstanceName=notebook_instance_name,
    InstanceType=instance_type,
    RoleArn=role_arn,
    SubnetId=subnet_id,
    SecurityGroupIds=security_group_ids
)

print(response)