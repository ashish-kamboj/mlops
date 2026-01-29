text = """
### Description ::
---------------
DAG description what it does?

### Details ::
-----------
1. Detail about each individual tasks 

"""

## Importing Libraries
import airflow
from airflow import DAG
from airflow.contrib.operators.ecs_operator import ECSOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
import logging

## Add logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Getting DAG variables
dag_base_path = Variable.get("dag_base_path")
aws_key = Variable.get("secret_access_key")
aws_secret = Variable.get("secret_key")
region = Variable.get("region")

## General AWS and AWS ECS related parameters
awsRegionName = Variable.get("region")
awsCluster = "DataLoad"
awsTaskDefinition = "aws_task_definition_name"
awsContainerName = "aws_container_name"
awsNetworkSubnet = "subnet-************ec901"
AIRFLOW_ECS_OPERATOR_RETRIES = 1

ecs_operator_args_template = {
    "aws_conn_id": "aws_vpc",
    "region_name": awsRegionName,
    "launch_type": "FARGATE",
    "cluster": awsCluster,
    "task_definition": awsTaskDefinition,
    "network_configuration": {
        "awsvpcConfiguration": {
            "assignPublicIp": "ENABLED",
            "subnets": [awsNetworkSubnet],
        }
    },
    "awslogs_group": "/ecs/" + awsTaskDefinition,
    "awslogs_stream_prefix": "ecs/" + awsContainerName,
}


## Create DAG
dag_name = "some_dag_name"
args = {
    "owner": "owner_name",
    "start_date": airflow.utils.dates.days_ago(1),
    "email": ['sometext@example.com'],
    "email_on_failure": False,
    #"on_failure_callback": some_function,
}

dag = DAG(
    dag_name,
    default_args=args,
    schedule_interval=None,
    template_searchpath=dag_base_path,
    tags=["tag1","tag2"],
)

# Add documentation for DAG
dag.doc_md = text

## Fuction for getting DAG parameters
def initiate_dag(**kwargs):
    ## Accessing parameters passed to the DAG (either from Airflow UI while triggering the DAG or triggering DAg from another DAG)
    variable_1 = kwargs['dag_run'].conf['variable_1']
    variable_2 = kwargs['dag_run'].conf['variable_2']
    variable_3 = kwargs['dag_run'].conf['variable_3']
    variable_4 = kwargs['dag_run'].conf['variable_4']
    
    kwargs["ti"].xcom_push(key="variable_1", value=variable_1)
    kwargs["ti"].xcom_push(key="variable_2", value=variable_2)
    kwargs["ti"].xcom_push(key="variable_3", value=variable_3)
    kwargs["ti"].xcom_push(key="variable_4", value=variable_4)


## Operation Definitions
with dag:

    initiate_dag = PythonOperator(
        task_id="initiate_dag",
        python_callable=initiate_dag,
        provide_context=True,
        dag=dag,
    )

    pipeline_task_1 = ECSOperator(
        provide_context=True,
        task_id="pipeline_task_1",
        dag=dag,
        **ecs_operator_args_template,
        overrides={
            "containerOverrides": [
                {
                    "name": awsContainerName,
                    "memoryReservation": 500,
                    "command": [
                        "python",
                        "part1_some_python_script_name.py"
                        ,
                        "{}".format("{{ task_instance.xcom_pull(key='variable_1') }}"),
                        "{}".format("{{ task_instance.xcom_pull(key='variable_2') }}"),
                        "{}".format("{{ task_instance.xcom_pull(key='variable_3') }}"),
                        "{}".format("{{ task_instance.xcom_pull(key='variable_4') }}"),
                    ],
                }
            ]
        }
    )

    pipeline_task_2 = ECSOperator(
        provide_context=True,
        task_id="pipeline_task_2",
        dag=dag,
        **ecs_operator_args_template,
        overrides={
            "containerOverrides": [
                {
                    "name": awsContainerName,
                    "memoryReservation": 500,
                    "command": [
                        "python",
                        "part2_some_python_script_name.py"
                        ,
                        "{}".format("{{ task_instance.xcom_pull(key='variable_1') }}"),
                        "{}".format("{{ task_instance.xcom_pull(key='variable_2') }}"),
                        "{}".format("{{ task_instance.xcom_pull(key='variable_3') }}"),
                        "{}".format("{{ task_instance.xcom_pull(key='variable_4') }}"),
                    ],
                }
            ]
        }
    )


    ## Define Flow Dependencies
    (
        initiate_dag
        >> pipeline_task_1
        >> pipeline_task_2
    )
