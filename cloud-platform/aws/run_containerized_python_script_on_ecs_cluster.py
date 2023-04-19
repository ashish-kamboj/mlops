## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1' # region where the table is located

## Specify the task definition and container details
cluster = 'cluster_name' #e.g. 'DataLoad'
task_definition = 'task_definition'
container_name = 'container_name'
command = ['python', 'example.py']
#memory = 256
#cpu = 128

## Initialize ECS client
ecs = boto3.client('ecs', 
                    region_name=region_name, 
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


# Run the container in the specified cluster
response = ecs.run_task(
    cluster=cluster,
    taskDefinition=task_definition,
    launchType='FARGATE',
    networkConfiguration={
        'awsvpcConfiguration':{
            'subnets':['subnet-0e00d00000a1ec111'],
            'assignPublicIp':'ENABLED'
        }
    },
    overrides={
        'containerOverrides': [
            {
                'name': container_name,
                'command': command,
                #'memory': memory,
                #'cpu': cpu
            }
        ]
    }
)

# Print the response
print(response)
