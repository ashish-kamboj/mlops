## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1' # region where the table is located
source_table_name = 'source_table_name'
destination_table_name = 'destination_table_name'

## Setting up the DynamoDB client
dynamodb = boto3.client('dynamodb', 
                        region_name=region_name, 
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Get the details of the source table
source_table = dynamodb.describe_table(TableName=source_table_name)['Table']

# Create a replica of the source table in the same region
replica_params = {
    'AttributeDefinitions': source_table['AttributeDefinitions'],
    'TableName': destination_table_name,
    'KeySchema': source_table['KeySchema'],
    'BillingMode': 'PROVISIONED', # or 'PAY_PER_REQUEST'
    'ProvisionedThroughput': {
        #'ReadCapacityUnits': source_table['ProvisionedThroughput']['ReadCapacityUnits'],
        #'WriteCapacityUnits': source_table['ProvisionedThroughput']['WriteCapacityUnits']
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    },
    #'StreamSpecification': source_table['StreamSpecification'],
    'SSESpecification': source_table.get('SSEDescription', {}).get('SSEEnabled', {})
}

dynamodb.create_table(**replica_params)

# Wait for the replica table to be created
waiter = dynamodb.get_waiter('table_exists')
waiter.wait(TableName=destination_table_name)

print(f'Replica table {destination_table_name} created in region {region_name}')