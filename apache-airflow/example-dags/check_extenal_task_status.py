from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.api.common.experimental.get_task_instance import get_task_instance
from airflow.models import DagRun
from datetime import datetime

def get_most_recent_dag_run(dag_id):
    dag_runs = DagRun.find(dag_id=dag_id)
    dag_runs.sort(key=lambda x: x.execution_date, reverse=True)
    return dag_runs[0] if dag_runs else None


default_args = {'start_date' : datetime(2023, 1, 1)}

def def_check_task_status(**kwargs):
    dag_id = kwargs['dag_id']
    task_id = kwargs['task_id']
    
    execution_date = get_most_recent_dag_run(dag_id).execution_date
    task_instance = get_task_instance(dag_id=dag_id, task_id=task_id, execution_date=execution_date)
    status = task_instance.current_state()
    print(f"Status of Task {task_id} in DAG {dag_id} : {status}")

with DAG('some_dag_id', 
        schedule_interval='@daily',
        default_args = default_args,
        catchup=False) as dag:

    check_task_status = PythonOperator(
        task_id='check_task_status',
        python_callable=def_check_task_status,
        op_kwargs={'dag_id': 'external_dag_d', 'task_id': 'external_task_id'},
        dag=dag)