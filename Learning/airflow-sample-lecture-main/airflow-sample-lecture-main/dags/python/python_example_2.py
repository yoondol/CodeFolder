from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# DAG 정의
dag = DAG(
    'python_example_2',
    description='My example DAG',
    tags=['example', 'python'],
    schedule_interval=timedelta(days=1),  # 매일 실행
    start_date=datetime(2024, 11, 1),
    catchup=False,  # 과거 실행에서 누락된 작업을 재실행하지 않음
)

# 작업 정의
def task1():
    print("Task 1")

def task2():
    print("Task 2")

# DAG에 작업 추가
t1 = PythonOperator(
    task_id='task1',
    python_callable=task1,
    dag=dag,
)

t2 = PythonOperator(
    task_id='task2',
    python_callable=task2,
    dag=dag,
)

# 의존성 정의
t1 >> t2