### Python code for interacting with various Azure services

| Azure Service |Action                                                           |Detail                         | References|
|---------------|-----------------------------------------------------------------|-------------------------------|-----------|
|Blob           |[Get blob SAS url](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/azure/scripts/blob_sas_url.py)  |Get public url to access blob for specified time period|   |
|File Share     |[Get File Share SAS url](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/azure/scripts/fileshare_sas_url.py)  |Get public url to access file share object for specified time period|   |
|Document Intelligence|[Extract text from document](https://github.com/ashish-kamboj/mlops/blob/main/cloud-platform/azure/scripts/extract_text_from_document_using_document_intelligence.py)|Extract text from the documents (pdf) present in AWS s3


### CI/CD Pipeline setup and Run Unit test using Azure DevOps
[YAML script](https://github.com/ashish-kamboj/mlops/cloud-platform/azure/scripts/azure-pipeline.yaml) to create CI Pipeline and run unit test cases on pull request using Azure DevOps. Also, find the yaml script explanation [here](https://github.com/ashish-kamboj/mlops/cloud-platform/azure/scripts/azure-pipeline-yaml-explanation.txt)

#### <ins>References</ins>
- [Azure Databricks CI/CD with Azure DevOps](https://www.youtube.com/watch?v=8SgHFXXdDBQ)
- [Configuring CI/CD Pipelines as Code with YAML in Azure DevOps](https://azuredevopslabs.com/labs/azuredevops/yaml/)
- [Run Python test with Azure DevOps pipeline](https://www.codewrecks.com/post/old/2018/11/run-python-test-with-azure-devops-pipeline/)
- [How to publish python unittest results to azure pipeline](https://stackoverflow.com/questions/72085550/how-to-publish-python-unittest-results-to-azure-pipeline)
- [azure-pipelines-python-examples](https://github.com/tonybaloney/azure-pipelines-python-examples/blob/master/basic-unittest.md)
- [Azure Pipelines with Python — by example](https://medium.com/@anthonypjshaw/azure-pipelines-with-python-by-example-aa65f4070634)
- [Publish Code Coverage on Azure Pipelines using Pytest & Cobertura Parser](https://python.plainenglish.io/publish-code-coverage-on-azure-pipelines-using-pytest-cobertura-parser-8838750e3c52)