## Importing Libraries
import boto3
from datetime import datetime, timedelta

## Set your AWS region and credentials
aws_region = 'ap-southeast-1'
AWS_ACCESS_KEY_ID = 'access_key_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'

## Set the age (in days) after which images should be removed
image_age_threshold = 30

## Function to delete older images from ECR
def remove_old_images():
    # Create an ECR client
    ecr_client = boto3.client('ecr', 
                              region_name=aws_region,
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Get a list of all repositories in the registry
    response = ecr_client.describe_repositories()
    repositories = response['repositories']

    # Iterate through each repository
    for repository in repositories:
        repository_name = repository['repositoryName']
        print(f"Processing repository: {repository_name}")

        # List all images in the repository
        response = ecr_client.list_images(repositoryName=repository_name)
        image_details = response['imageIds']

        # Count the number of images with tag "latest"
        latest_image_count = sum(1 for image in image_details if 'latest' in image.get('imageTag', ''))

        # Iterate through each image
        for image_detail in image_details:
            image_digest = image_detail['imageDigest']
            image_tags = image_detail.get('imageTag', '')

            # Skip images with tag "latest"
            if 'latest' in image_tags:
                continue

            # Describe the image to get the pushed timestamp
            response = ecr_client.describe_images(repositoryName=repository_name, imageIds=[{'imageDigest': image_digest}])
            image_pushed_at = response['imageDetails'][0]['imagePushedAt']
            
            # Parse the pushed timestamp into a datetime object
            pushed_datetime = datetime.strptime(image_pushed_at.strftime('%Y-%m-%dT%H:%M:%S.%f%z'), "%Y-%m-%dT%H:%M:%S.%f%z")

            # Calculate the age of the image
            image_age = datetime.now(pushed_datetime.tzinfo) - pushed_datetime

            # Check if the image exceeds the age threshold
            if image_age > timedelta(days=image_age_threshold) and latest_image_count >= 1:
                print(f"Removing image with digest: {image_digest}")

                # Remove the image from the repository
                ecr_client.batch_delete_image(repositoryName=repository_name,
                                              imageIds=[{'imageDigest': image_digest}])

# Execute the function to remove old images
remove_old_images()