from airflow import DAG
from airflow.operators.bash_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta


def dummy_task(**kwargs):
    pass

mail_content = """<p>Hi,</p>
<p>The following task has failed:</p>
<ul>
<li>DAG ID: {{ dag.dag_id }}</li>
<li>Task ID: {{ task.task_id }}</li>
<li>Execution Date: {{ execution_date }}</li>
<li>Log URL: <a href="{{ ti.log_url }}">Click here</a></li>
</ul>
<p>Please check the logs and take necessary actions.</p>
<p>Regards,</p>
<p>Airflow</p>
"""

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 25),
    'email': ['user@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(dag_id='send_email_on_success_failure', 
          default_args=default_args, 
          schedule_interval='@daily'
          )

# Define a task that may fail
task1 = PythonOperator(
    task_id='task1',
    provide_context=True,
    python_callable=dummy_task,
    dag=dag
    )

task2 = PythonOperator(
    task_id='task2',
    provide_context=True,
    python_callable=dummy_task,
    dag=dag
    )

# Define a task that will send an email notification on success of task1
success_task = EmailOperator(
    task_id='success_task',
    to='user@example.com',
    subject='Task Success Notification',
    html_content=mail_content,
    trigger_rule=TriggerRule.ALL_SUCCESS,
    dag=dag
    )

# Define a task that will send an email notification on failure of task1
failure_task = EmailOperator(
    task_id='failure_task',
    to='user@example.com',
    subject='Task Failure Notification',
    html_content=mail_content,
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag
    )

# Set the dependency between the tasks
task1 >> task2 >> success_task >> failure_task

