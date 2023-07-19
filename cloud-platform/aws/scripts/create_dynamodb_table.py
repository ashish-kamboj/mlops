## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1' # region where the table is located

# Specify the name of the DynamoDB table
table_name = 'table_name'

## Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', 
                        region_name=region_name, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[
        {
            'AttributeName': 'partition-key', #e.g. 'id'
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'sort-key', #e.g. 'updated_date'
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'partition-key',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'sort-key',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

print("Table status:", table.table_status)
