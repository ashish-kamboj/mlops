## Importing Libraries
import boto3

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

# Define the list of items to be added to the table
items_to_add = [
    {'id': {'N': '1'}, 'name': {'S': 'name1'}, 'age': {'N': '30'}, 'updated_date': {'S': '2023-03-28'}},
    {'id': {'N': '2'}, 'name': {'S': 'name2'}, 'age': {'N': '25'}, 'updated_date': {'S': '2023-03-28'}},
    {'id': {'N': '3'}, 'name': {'S': 'name3'}, 'age': {'N': '40'}, 'updated_date': {'S': '2023-03-28'}}
]

for item in items_to_add:
    response = dynamodb.batch_write_item(
        RequestItems = {
            table_name: [
                {
                    "PutRequest": {"Item" : item}
                }
            ]
        }
    )