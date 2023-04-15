## Importing Libraries
import boto3

## Constants
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

region_name = 'us-east-1' # region where the table is located

# Specify the sender and recipient email addresses
sender = 'sender@example.com'
recipient = 'recipient@example.com'

## Initialize SES client
ses = boto3.client('ses', 
                    region_name=region_name, 
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

response = ses.send_email(
    Source=sender,
    Destination = {
        'ToAddresses': [recipient]
    },
    Message = {
        'Body':{
            'Text':{
                'Data': 'This is a test email from Amazon SES.'
            }
        },
        'Subject':{
            'Data': 'Amazon SES Test Email'
        }
    }
)