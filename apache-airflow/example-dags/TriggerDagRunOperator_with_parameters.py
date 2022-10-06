from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import uuid


def initiate_dag(**kwargs):
    param1 = kwargs['dag_run'].conf.get('param1')
    param2 = kwargs['dag_run'].conf.get('param2')

    kwargs["task_instance"].xcom_push(key="param1", value=param1)
    kwargs["task_instance"].xcom_push(key="param2", value=param2)

def data_processing_task():
    print('Data Processing Completed!')

def trigger_target_dag(**kwargs):
    trigger_params={}
    trigger_params['param1'] = kwargs['task_instance'].xcom_pull(key='param1')
    trigger_params['param2'] = kwargs['task_instance'].xcom_pull(key='param2')    

    TriggerDagRunOperator(
        task_id='trigger_target',
        trigger_dag_id='target_dag_id',
        trigger_run_id=str(uuid.uuid1()),
        execution_date=str(datetime.utcnow()),
        conf=trigger_params
    ).execute(kwargs)
    

default_args = {
    'owner':'owner_name',
    'start_date': datetime(2021, 1, 1),
    'email':['some_name@example.com'],
    'email_on_failure':False
}

with DAG('trigger_dag', 
    schedule_interval='@daily', 
    default_args=default_args, 
    catchup=False) as dag:

    initiate_dag = PythonOperator(
        task_id='initiate_dag',
        python_callable=initiate_dag
    )

    data_processing_task = PythonOperator(
        task_id='data_processing_task',
        python_callable=data_processing_task
    )

    trigger_target_dag = PythonOperator(
        task_id='trigger_target_dag',
        python_callable=trigger_target_dag
    )

    initiate_dag >> data_processing_task >> trigger_target_dag