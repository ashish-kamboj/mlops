## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1' # region where the table is located
source_table_name = 'source_table_name'
destination_table_name = 'destination_table_name'

## Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', 
                        region_name=region_name, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Scan the source table and get all items
response = dynamodb.scan(TableName=source_table_name)
items = response['Items']

# Create a list of requests for batch write
requests = []
for item in items:
    requests.append({'PutRequest': {'Item': item}})

# Send the batch write request to the destination table
response = dynamodb.batch_write_item(
    RequestItems={
        destination_table_name: requests
    }
)

print(f"Processed {len(response['UnprocessedItems'])} unprocessed items")