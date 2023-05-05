from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime


default_args = {
    'start_date': datetime(2023, 5, 5),
    'retries': 0
}

regions = Variable.get('regions', default_var='region1,region2,region3,region4').split(',')

## Task1 Function
def task1_code(**kwargs):
    print(f"This is the code for Task1 - Region:{kwargs['region']}")

## Task2 Function
def task2_code(**kwargs):
    print(f"This is the code for Task1 - Region:{kwargs['region']}")


with DAG('first_dag', default_args=default_args, schedule_interval=None) as dag:

    ## Define a task to trigger the second DAG
    trigger_second_dag = TriggerDagRunOperator(
        task_id='trigger_second_dag',
        trigger_dag_id='second_dag',
        trigger_rule='all_success',
        dag=dag,
    )

    task_ids = []
    for region in regions:
        task_1 = PythonOperator(
            task_id=f'task_1_{region}',
            python_callable=task1_code,
            op_kwargs={'region': region},
            provide_context=True,
        )
        task_2 = PythonOperator(
            task_id=f'task_2_{region}',
            python_callable=task2_code,
            op_kwargs={'region': region},
            provide_context=True,
        )

        ## Setting the dependency
        task_1 >> task_2 >> trigger_second_dag

