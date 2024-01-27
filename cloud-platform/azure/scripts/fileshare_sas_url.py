from azure.storage.fileshare import generate_share_sas, ShareSasPermissions
from datetime import datetime, timedelta

account_name = "<<account_name>>"
account_key = "<<account_key>>"
share_name = "<<share_name>>"
file_path = "sample.pdf"

def generate_fileshare_sas_url(account_name, share_name, file_path, account_key):
    sas_token = generate_share_sas(
        account_name=account_name,
        share_name=share_name,
        account_key=account_key,
        permission=ShareSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)  # Set the expiry time as needed
    )
    file_url = f"https://{account_name}.file.core.windows.net/{share_name}/{file_path}?{sas_token}"
    return file_url

print(generate_fileshare_sas_url(account_name, share_name, file_path, account_key))