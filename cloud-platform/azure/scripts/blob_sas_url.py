from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

account_name = "<<account_name>>"
container_name = "<<container_name>>"
blob_name = "sample.pdf"
account_key = "<<account_key>>"

def generate_blob_sas_url(account_name, container_name, blob_name, account_key):
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)  # Set the expiry time as needed
    )
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    return blob_url

print(generate_blob_sas_url(account_name, container_name, blob_name, account_key))