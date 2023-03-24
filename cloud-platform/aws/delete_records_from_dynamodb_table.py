## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1' # region where the table is located
table_name = 'table_name'

## Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', 
                        region_name=region_name, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Specify the name of the DynamoDB table and a list of keys of the items to be deleted
table_name = 'Table_name'
keys = [
    {'id': {'S': '123'}, 'timestamp': {'N': '1623032595'}},
    {'id': {'S': '456'}, 'timestamp': {'N': '1623032667'}}
]

# Create a list of requests for batch write
requests = []
for key in keys:
    requests.append({'DeleteRequest': {'Key': key}})

# Call the batch_write_item() method to delete the items from the table
response = dynamodb.batch_write_item(
    RequestItems={
        table_name: requests
    }
)

# Print the response
print(response)