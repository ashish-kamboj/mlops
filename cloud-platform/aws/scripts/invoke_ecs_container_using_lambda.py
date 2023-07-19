import boto3

def lambda_handler(event, context):
  client = boto3.client('ecs')
  

  response = client.run_task(
  cluster='DataLoad', # name of the cluster
  launchType = 'FARGATE',
  taskDefinition=event['jobname'], # replace with your task definition name and revision
  overrides={"containerOverrides": [{
            "name": event['jobname']
            }]},
  count = 1,
  platformVersion='LATEST',
  networkConfiguration={
        'awsvpcConfiguration': {
            'subnets': [
                'subnet-0e3xxxxxxxxxxxxxx',
                'subnet-002xxxxxxxxxxxxxx' # Second is optional, but good idea to have two
            ],

            'assignPublicIp': 'ENABLED'
        }
    })
  return str(response)
