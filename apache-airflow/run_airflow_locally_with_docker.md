
### Step 1:Install Docker  
 - Installation [Link](https://docs.docker.com/get-docker/)
 - Choose installer for Mac/Windows/Linux <br>
 
### Step 2: Install docker-compose  
By default it's already installed with docker, check the attached link incase if further setup is required - [Link](https://docs.docker.com/compose/install/) <br>
Create  new directory (let's say `airflow-docker`)
```sh
mkdir airflow-docker
cd airflow-docker
```
Run below command to download the docker-compose file in `airflow-docker` folder
```sh
curl -LfO “http://apache-airflow-docs.s3-website.eu-central-1.amazonaws.com/docs/apache-airflow/latest/docker-compose.yaml”
```

### Step 3:Create Directories  
Open `airflow-docker` folder (having **.yaml** file) in code editor (e.g. VSCode) and create three directories **dags/logs/plugins** <br>

<ins>**For Linux**</ins>
```sh
mkdir ./dags ./logs ./plugins
```
<ins>**For Windows**</ins>
```sh
mkdir dags logs plugins
```
### Step 4:Setting the Airflow user or setup environment variables  
Needs to export an environment variable to ensure that the folder on your host machine and the folders within the containers share the same permissions <br>

<ins>**For Linux**</ins>
```sh
echo -e "AIRFLOW_UID=**$(**id -u**)**\nAIRFLOW_GID=0" > .env
```
<ins> **For Windows**</ins>
 - Create **.env** file
 - Add **AIRFLOW_UID=50000** and **AIRFLOW_GID=0** in
   **.env** file

### Step 5: Start docker  
Start docker if installed first time in Windows <br>

### Step 6:Initialize Airflow Instance or Database  
It runs `airflow db init` and `airflow db upgrade`, also creates a airflow admin user with default credentials **username**=airflow and **password**=airflow 
```sh
docker-compose up airflow-init
```
<ins>**Resolving Errors**</ins>

**Error_1**  
![Airflow Initialization Error-1](https://github.com/ashish-kamboj/mlops/blob/main/apache-airflow/images/airflow_initilization_error.png)

**Solution_1**  
Follow the link to resolve - [Link](https://stackoverflow.com/questions/58663920/can-i-run-docker-desktop-on-windows-without-admin-privileges#:~:text=If%20your%20admin%20account%20is,the%20changes%20to%20take%20effect.) <br>

**Error_2**  
![Airflow Initialization Error-2](https://github.com/ashish-kamboj/mlops/blob/main/apache-airflow/images/airflow_initilization_error_2.png)

**Solution_2**  
![Airflow Initialization Error-2 Solution](https://github.com/ashish-kamboj/mlops/blob/main/apache-airflow/images/airflow_initilization_error_2_solution.png)

### Step 7: Start Airflow Services  
To get airflow up and running, basically to start all the services needed to run airflow
```sh
docker-compose up
```

In order to check the running status of services, run below command
```sh
docker ps
```

### Step 8:Access Airflow UI  
Open Airflow UI - [http://localhost:8080](http://localhost:8080) with Username/Password = airflow/airflow
