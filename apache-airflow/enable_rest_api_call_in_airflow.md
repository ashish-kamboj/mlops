### Airflow v1.10.11
1. <ins>**[api]**  changes:</ins>  
Change **auth_backend**`auth_backend=airflow.api.auth.backend.deny_all` to `auth_backend=airflow.contrib.auth.backends.password_auth`

2. <ins>**[webserver]** changes:</ins>   
Correct **base_url**=<<some base_url , something http://10.10.10.10:8080>>   
Set **authenticate**=True   
Set **rbac**=True   

3. <ins>**Create User**</ins>    
- **Through CLI**   
airflow create_user -r Admin -u admin -e admin@admin.com -f admin -l admin -p admin   
- **Through Python code** - [Link](https://github.com/ashish-kamboj/mlops/blob/main/apache-airflow/example-dags/create_user_for_rest_api_calls.py)
