## Importing Libraries
import airflow
from airflow import DAG
from airflow import models, settings
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.auth.backends.password_auth import PasswordUser
import logging

# BASE CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

## Create DAG
dag_id = "dag_id_create_user"
args = {
    "owner": "owner_name",
    "start_date": airflow.utils.dates.days_ago(1),
    "email": ['xyz@example.com'],
    "email_on_failure": False,
}

dag = DAG(
    dag_id,
    default_args=args,
    schedule_interval=None,
    tags=["API Calls","Create user"],
)

def def_create_user(**kwargs):
    user = PasswordUser(models.User())
    user.username = kwargs['dag_run'].conf['username']
    user.email = kwargs['dag_run'].conf['email']
    user.password = kwargs['dag_run'].conf['password']
    session = settings.Session()
    session.add(user)
    session.commit()
    session.close()

## Operation Definitions
with dag:
    create_user = PythonOperator(
        task_id="create_user",
        python_callable=def_create_user,
        provide_context=True,
        dag=dag,
    )

    ## Define Flow Dependencies
    create_user