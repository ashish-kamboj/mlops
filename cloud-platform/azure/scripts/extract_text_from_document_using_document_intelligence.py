## Importing Libraries
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
import boto3

## AWS Key's
AWS_ACCESS_KEY_ID = '<<access_key_id>>'
AWS_SECRET_ACCESS_KEY = '<<secret_access_key>>'

# Specify the S3 bucket name and object key (path)
AWS_S3_BUCKET_NAME = "<<some-bucket-name>>"
AWS_S3_OBJECT_KEY = '<<some/file/path/sample.pdf>>'

# set `<your-endpoint>` and `<your-key>` variables with the values from the Azure portal
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = "<<https://doc-intelligence-test.cognitiveservices.azure.com/>>"
AZURE_DOCUMENT_INTELLIGENCE_KEY = "<<doc-intelligence-key>>"


## Generating pre-signed url for document in AWS s3
def generate_s3_presigned_url(aws_access_key_id, aws_secret_access_key, bucket_name, object_key):

    ## Creating s3 client object
    s3_client = boto3.client('s3',
                        region_name='us-east-1',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=3600  # URL will expire in 1 hour (3600 seconds)
    )

    return url


## Extracting text from document present in AWS s3(by using pre-signed url)
def extract_text_from_documents(endpoint, key):

    url = generate_s3_presigned_url(aws_access_key_id=AWS_ACCESS_KEY_ID, 
                                    aws_secret_access_key=AWS_S3_OBJECT_KEY, 
                                    bucket_name=AWS_S3_BUCKET_NAME, 
                                    object_key=AWS_S3_OBJECT_KEY)
    
    formUrl = {"urlSource": url}

    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout", formUrl
    )

    result = poller.result()

    return result['content']


if __name__ == "__main__":
    document_content = extract_text_from_documents(endpoint=AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, 
                                                   key=AZURE_DOCUMENT_INTELLIGENCE_KEY)
    
    print(document_content)