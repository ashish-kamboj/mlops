### Python code for interacting with various AWS services

|AWS Service     |Action     |Detail    |Reference     |
|:---------------|:----------|:---------|:-------------|
|                |[Get AWS access and secret key](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/get_aws_access_and_secret_key.py)|   |     |
|CodePipeline, ECS, Lambda|[Create ECS task definition Using Lambda for CodePipeline](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/create_ecs_task_definition_using_lambda_for_codepipeline.py)|1. Creates Log Group for ECS task definition in Cloudwatch <br> 2. Creates ECS task definition <br> 3. Invokes another lambda, which triggers ECS task <br> 4. Send Success and Failure notification to AWS Codepipeline   |   |
|DynamoDB        |[Create DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/create_dynamodb_table.py)|New table   |    |
|DynamoDB        |[Create existing table replica](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/create_dynamodb_table_replica_in_same_region.py)|In same region   |    |
|DynamoDB        |[Delete records from DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/delete_records_from_dynamodb_table.py)|Delete multiple records   |    |
|DynamoDB        |[Delete DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/delete_dynamodb_table.py)|  |    |
|DynamoDB        |[Get data from DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/get_data_from_dynamodb_table.py)|   |    |
|DynamoDB        |[Insert data from one table to another table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/insert_data_from_one_dynamodb_to_another_dynamodb_table.py)|In same region   |   |
|DynamoDB        |[Insert records in DynamoDB table](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/insert_records_to_dynamodb_table.py)|Can specify additional columns, accordingly the table structure will modify   |   |
|Lambda, ECS     |[Invoke ECS container using Lambda](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/invoke_ecs_container_using_lambda.py)| | |
ECS              |[Run containerized python script on ECS cluster](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/run_containerized_python_script_on_ecs_cluster.py)|  |  |
|s3              |[Checking whether a file is present or not in s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/check_file_exists_in_s3.py)       |          |              |
|s3              |[Delete file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/delete_file_from_s3.py)|   |   |
|s3              |[Delete all objects from s3 folder](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/delete_all_objects_from_s3_folder.py)|   |   |
|s3              |[Get latest file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/get_latest_file_from_s3.py)|        |       |
|s3              |[Get latest file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/get_latest_file_from_s3_2.py)|Using Pagination as directory has over 1000 objects|   |
|s3              |[Get latest file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/get_latest_file_from_s3_3.py)|Using Pagination as directory has over 1000 objects along with file pattern filter|   |
|s3              |[Put data as a pickle file in s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/upload_data_as_pickle_to_s3_1.py)|Using Object.put()  |    |
|s3              |[Put data as a pickle file in s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/upload_data_as_pickle_to_s3_2.py)|Using Client.put_object()  |    |
|s3              |[Read csv file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/read_csv_file_from_s3.py)|     |       |
|s3              |[Read Excel(xlsx) file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/read_excel_file_from_s3.py)|      |        |
|s3              |[Read pickle(pkl) file from s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/read_pickle_file_from_s3.py)|      |          |
|s3              |[Save dataframe as csv to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/save_dataframe_as_csv_to_s3.py)|      |          |
|s3              |[Save dataframe as Excel(xlsx) to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/save_dataframe_as_excel_to_s3.py)|      |          |
|s3              |[Upload file from local to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/upload_file_from_local_to_s3.py)|      |          |
|s3              |[Upload list of files from local to s3](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/upload_list_of_files_from_local_to_s3.py)|      |          |
|s3, Lambda      |[Download and Execute python file from s3 using Lambda](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/download_and_execute_python_file_from_s3_using_lambda.py)|         |          |
|Sagemaker       |[Create Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/create_sagemaker_notebook_instance.py)|   |    |
|Sagemaker       |[Delete Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/delete_sagemaker_notebook_instance.py)|   |   |
|Sagemaker       |[Describe Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/describe_sagemaker_notebook_instance.py)|Detail about notebook instance   |    |
|Sagemaker       |[List Notebook Instances](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/list_sagemaker_notebook_instances.py)|List all the available notebook instances   |   |
|Sagemaker       |[Start Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/start_sagemaker_notebook_instance.py)|   |    |
|Sagemaker       |[Stop Notebook Instance](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/stop_sagemaker_notebook_instance.py)|   |    |
|SES             |[Send Email notification](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/aws/send_email_notification_using_ses.py)|Amazon SES is case-sensitive|  |
