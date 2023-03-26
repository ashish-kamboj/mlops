## Importing Libraries
import boto3
from boto3.dynamodb.types import TypeDeserializer

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1' # region where the table is located

# Specify the name of the DynamoDB table
table_name = 'table_name'

## Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', 
                        region_name=region_name, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'name',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'details_updated',
            'AttributeType': 'BOOL'
        },
        {
            'AttributeName': 'updated_date',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

print("Table status:", table.table_status)
