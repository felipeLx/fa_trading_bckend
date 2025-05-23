from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

continuous_dag = DAG(
    dag_id = 'continuous_robot',
    default_args=default_args,
    description='Run the robot logic frequently to check for trade signals',
    schedule='* 13-20 * * 1-5',  # Every minute, Mon-Fri, 13:00-20:59 UTC (market hours)
    start_date=datetime(2025, 5, 21),
    catchup=False,
)

run_robot = BashOperator(
    task_id='run_robot',
    bash_command='python3 /mnt/c/Users/USUARIO/Desktop/workspace/fa_trading_bckend/robot.py',
    dag=continuous_dag,
)

globals()["continuous_dag"] = continuous_dag