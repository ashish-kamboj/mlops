text = """
### Description ::
---------------
DAG for triggering another DAG (without passing parameters to another DAG)

### Details ::
-----------
1. Getting Run arguments
2. Performing data processing
3. Trigger next DAG after data processing
"""

## Importing Libraries
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
from datetime import datetime


## Function for getting DAG parameters
def initiate_dag(**kwargs):
    param1 = kwargs['dag_run'].conf.get('param1')
    param2 = kwargs['dag_run'].conf.get('param2')

    kwargs["task_instance"].xcom_push(key="param1", value=param1)
    kwargs["task_instance"].xcom_push(key="param2", value=param2)


## Function for performing data processing
def data_processing_task():
    print('Data Processing Completed!')
    

## DAG default arguments
default_args = {
    'owner':'owner_name',
    'start_date': datetime(2021, 1, 1),
    'email':['some_name@example.com'],
    'email_on_failure':False
}


## Creating DAG and defining operator definition
with DAG('trigger_dag', 
    schedule_interval='@daily', 
    default_args=default_args, 
    catchup=False) as dag:

    # Add documentation for DAG
    dag.doc_md = text

    initiate_dag = PythonOperator(
        task_id='initiate_dag',
        python_callable=initiate_dag,
        provide_context=True
    )

    data_processing_task = PythonOperator(
        task_id='data_processing_task',
        python_callable=data_processing_task
    )

    trigger_target_dag = TriggerDagRunOperator(
        task_id='trigger_target_dag',
        trigger_dag_id='target_dag',
        execution_date = '{{ ds }}'
    )

    ## Defining Flow Dependencies
    initiate_dag >> data_processing_task >> trigger_target_dag