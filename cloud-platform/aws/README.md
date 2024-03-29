### Python code for interacting with various AWS services

|AWS Service     |Action     |Detail    |Reference     |
|:---------------|:----------|:---------|:-------------|
|                |[Get AWS access and secret key](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/get_aws_access_and_secret_key.py)|   |     |
|CodePipeline, ECS, Lambda|[Create ECS task definition Using Lambda for CodePipeline](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/create_ecs_task_definition_using_lambda_for_codepipeline.py)|1. Creates Log Group for ECS task definition in Cloudwatch <br> 2. Creates ECS task definition <br> 3. Invokes another lambda, which triggers ECS task <br> 4. Send Success and Failure notification to AWS Codepipeline   |   |
|DynamoDB        |[Create DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/create_dynamodb_table.py)|New table   |    |
|DynamoDB        |[Create existing table replica](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/create_dynamodb_table_replica_in_same_region.py)|In same region   |    |
|DynamoDB        |[Delete records from DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/delete_records_from_dynamodb_table.py)|Delete multiple records   |    |
|DynamoDB        |[Delete DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/delete_dynamodb_table.py)|  |    |
|DynamoDB        |[Get data from DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/get_data_from_dynamodb_table.py)|   |    |
|DynamoDB        |[Insert data from one table to another table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/insert_data_from_one_dynamodb_to_another_dynamodb_table.py)|In same region   |   |
|DynamoDB        |[Insert records in DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/insert_records_to_dynamodb_table.py)|Can specify additional columns, accordingly the table structure will modify   |   |
|ECR             |[Remove older images](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/remove_older_images_from_ecr.py)|Keep the image with tag **latest**  |   |
|Lambda, ECS     |[Invoke ECS container using Lambda](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/invoke_ecs_container_using_lambda.py)| | |
ECS              |[Run containerized python script on ECS cluster](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/run_containerized_python_script_on_ecs_cluster.py)|  |  |
|s3              |[Checking whether a file is present or not in s3](https://github.com/ashish-kamboj/mlops/blob/main/scripts/cloud-platform/aws/check_file_exists_in_s3.py)       |          |              |
|s3              |[Delete file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/delete_file_from_s3.py)|   |   |
|s3              |[Delete all objects from s3 folder](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/delete_all_objects_from_s3_folder.py)|   |   |
|s3              |[Get latest file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/get_latest_file_from_s3.py)|        |       |
|s3              |[Get latest file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/get_latest_file_from_s3_2.py)|Using Pagination as directory has over 1000 objects|   |
|s3              |[Get latest file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/get_latest_file_from_s3_3.py)|Using Pagination as directory has over 1000 objects along with file pattern filter|   |
|s3              |[Get list of subfolder from s3 file paths](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/get_list_of_subfolders_from_s3.py)|Assuming subfolder at specific position|    |
|s3              |[Get presigned url of s3 obkect](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/get_presigned_url_of_s3_object.py)|    |    |
|s3              |[Put data as a pickle file in s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/upload_data_as_pickle_to_s3_1.py)|Using Object.put()  |    |
|s3              |[Put data as a pickle file in s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/upload_data_as_pickle_to_s3_2.py)|Using Client.put_object()  |    |
|s3              |[Read csv file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/read_csv_file_from_s3.py)|     |       |
|s3              |[Read Excel(xlsx) file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/read_excel_file_from_s3.py)|      |        |
|s3              |[Read pickle(pkl) file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/read_pickle_file_from_s3.py)|      |          |
|s3              |[Save dataframe as csv to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/save_dataframe_as_csv_to_s3.py)|      |          |
|s3              |[Save dataframe as Excel(xlsx) to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/scripts/aws/save_dataframe_as_excel_to_s3.py)|      |          |
|s3              |[Upload file from local to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/upload_file_from_local_to_s3.py)|      |          |
|s3              |[Upload list of files from local to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/upload_list_of_files_from_local_to_s3.py)|      |          |
|s3, Lambda      |[Download and Execute python file from s3 using Lambda](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/download_and_execute_python_file_from_s3_using_lambda.py)|         |          |
|Sagemaker       |[Create Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/create_sagemaker_notebook_instance.py)|   |    |
|Sagemaker       |[Delete Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/delete_sagemaker_notebook_instance.py)|   |   |
|Sagemaker       |[Describe Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/describe_sagemaker_notebook_instance.py)|Detail about notebook instance   |    |
|Sagemaker       |[List Notebook Instances](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/list_sagemaker_notebook_instances.py)|List all the available notebook instances   |   |
|Sagemaker       |[Start Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/start_sagemaker_notebook_instance.py)|   |    |
|Sagemaker       |[Stop Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/stop_sagemaker_notebook_instance.py)|   |    |
|Sagemaker       |[List training Jobs](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/list_sagemaker_training_jobs.py)|   |    |
|Sagemaker       |[Describe training Job](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/describe_sagemaker_training_job.py)|   |    |
|Sagemaker       |[List Models](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/list_sagemaker_models.py)|   |    |
|Sagemaker       |[Describe Model](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/describe_sagemaker_model.py)|   |    |
|SES             |[Send Email notification](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/scripts/send_email_notification_using_ses.py)|Amazon SES is case-sensitive|  |
