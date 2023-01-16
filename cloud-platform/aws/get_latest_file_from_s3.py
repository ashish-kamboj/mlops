import boto3

## Create s3 object
s3 = boto3.client('s3')

## Specify Bucket name and Prefix(folder path inside bucket)
BUCKET_NAME = 'bucket_name'
PREFIX = 'folder1/inside_folder_1' #Optional

## Get "Last Modified" date of each s3 object
get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))

## get list of objects from specified bucket (or prefix if specified)
response = s3.list_objects_v2(Bucket=BUCKET_NAME, 
                              Prefix=PREFIX)
objs = response['Contents']

## Sorted all the objects based on Last Modified date(latest change be the first element)
## Extract the latest modified object
lastest_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified, reverse=True)][0]
lastest_added