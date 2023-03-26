## Importing Libraries
import boto3

## AWS Key's
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

## Define DynamoDB table name
table_name = 'table_name'

## Creating s3 resource object
dynamodb_client= boto3.resource(
                'dynamodb',
                region_name='us-east-1',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

## Get DynamoDB table
table = dynamodb_client.Table(table_name)

## Get all items from DynamoDB table
response = table.scan()

## Print all items
for item in response['Items']:
    print(item)
