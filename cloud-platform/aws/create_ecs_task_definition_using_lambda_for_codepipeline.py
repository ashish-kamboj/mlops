import json
import boto3
 
# Define the client to interact with AWS Lambda
client = boto3.client('lambda')
code_pipeline = boto3.client('codepipeline')
ecs_client = boto3.client('ecs')
cloudwatch_client = boto3.client('logs')
 
def lambda_handler(event, context):
 
    try:
        # Extract the Job ID
        job_id = event['CodePipeline.job']['id']
 
        # Extract the Job Data
        data = event['CodePipeline.job']['data']
        print(data)
        data = json.loads(data['actionConfiguration']
                          ['configuration']['UserParameters'])
        job_data = data['jobname']
        memory = data['memory']
        cpu = data['cpu']
        inputParams = {
            "jobname": job_data
        }
        try:
            response = cloudwatch_client.create_log_group(
                logGroupName="/ecs/"+job_data)
        except Exception as ex1:
            print('Failed to create log group, ' + str(ex1))
        try:
            response = ecs_client.register_task_definition(
                executionRoleArn="arn:aws:iam::724876290804:role/ecsTaskExecutionRole",
                taskRoleArn="arn:aws:iam::724876290804:role/ecsTaskExecutionRole",
                containerDefinitions=[
                    {"name": job_data,
                     "image": "724876290804.dkr.ecr.ap-southeast-1.amazonaws.com/" + job_data+":latest",
                     "essential": True,
                     "logConfiguration":
                     {
                         "logDriver": "awslogs",
                         "options": {
                             "awslogs-group": "/ecs/" + job_data,
                             "awslogs-region": "ap-southeast-1",
                             "awslogs-stream-prefix": "ecs"
                         }
                     }
                     }],
                family=job_data,
                requiresCompatibilities=["FARGATE"],
                networkMode="awsvpc",
                memory=memory,
                cpu=cpu)
        except Exception as ex:
            print('Failed to register task, ' + str(ex))
 
        response = client.invoke(
            FunctionName='arn:aws:lambda:ap-southeast-1:724876290804:function:'+job_data,
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
 
        responseFromChild = json.load(response['Payload'])
 
        print('\n')
        put_job_success(job_id, 'successful')
 
    except Exception as e:
        # If any other exceptions which we didn't expect are raised
        # then fail the job and log the exception message.
        print('Function failed due to exception.')
        print(e)
        put_job_failure(job_id, 'Function exception: ' + str(e))
 
    print('Function complete.')
    return "Complete."
 
def put_job_success(job, message):
    """Notify CodePipeline of a successful job
 
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
 
    Raises:
        Exception: Any exception thrown by .put_job_success_result()
 
    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)
 
def put_job_failure(job, message):
    """Notify CodePipeline of a failed job
 
    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status
 
    Raises:
        Exception: Any exception thrown by .put_job_failure_result()
 
    """
    print('Putting job failure')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={
                                         'message': message, 'type': 'JobFailed'})