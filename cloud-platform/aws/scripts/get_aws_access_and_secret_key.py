## Importing Libraries
import boto3

## Getting Credentials
cred = boto3.Session().get_credentials()

ACCESS_KEY = cred.access_key
SECRET_KEY = cred.secret_key
SESSION_TOKEN = cred.token
