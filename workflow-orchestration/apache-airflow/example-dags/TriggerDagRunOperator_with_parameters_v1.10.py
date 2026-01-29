from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
from datetime import datetime


def initiate_dag(**kwargs):
    param1 = kwargs['dag_run'].conf.get('param1')
    param2 = kwargs['dag_run'].conf.get('param2')

    kwargs['task_instance'].xcom_push(key='param1', value=param1)
    kwargs['task_instance'].xcom_push(key='param2', value=param2)

def data_processing_task():
    print('Data Processing Completed!')

def trigger_target_dag_params(context, dag_run_obj):
    dag_run_obj.payload = {
                            'param1': context['task_instance'].xcom_pull(key='param1'),
                            'param2': context['task_instance'].xcom_pull(key='param2')
                            }
    
    return dag_run_obj
    

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

    trigger_target_dag = TriggerDagRunOperator(
        task_id='trigger_target_dag',
        execution_date=str(datetime.utcnow()),
        python_callable=trigger_target_dag_params,
        provide_context=True
    )

    initiate_dag >> data_processing_task >> trigger_target_dag