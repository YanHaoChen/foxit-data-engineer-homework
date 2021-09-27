import os
import sys
from functools import wraps

from airflow.utils.dates import days_ago
from airflow.settings import AIRFLOW_HOME
from airflow import DAG
from airflow.operators.bash import BashOperator


class EnvSetting(object):
    PROJECT_HOME = f'{AIRFLOW_HOME}/dags/foxit-homework'

    @staticmethod
    def append_project_to_path(f):
        @wraps(f)
        def insert_path(*args, **kwds):
            sys.path.insert(0, EnvSetting.PROJECT_HOME)
            return f(*args, **kwds)

        return insert_path


args = {
    'owner': 'sean',
}

dag = DAG(
    dag_id='setup_foxit_homework',
    default_args=args,
    schedule_interval='@once',
    start_date=days_ago(1),
)

check_requirements = BashOperator(
    task_id='check_requirements',
    bash_command=f'pip3 install -r {EnvSetting.PROJECT_HOME}/airflow_requirements.txt',
    depends_on_past=True,
    dag=dag
)

check_requirements