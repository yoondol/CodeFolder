from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
# from error_alarm import run_slack_alarm

# 기본 인자 설정
default_args = {
    'owner': 'airflow',  # DAG의 소유자
    'depends_on_past': False,  # 이전 DAG 실행 여부에 상관없이 실행
    'start_date': datetime(2024, 11, 15),  # DAG 시작 날짜
    'email_on_failure': False,  # 실패 시 이메일 알림 여부
    'email_on_retry': False,  # 재시도 시 이메일 알림 여부
    'retries': 3,  # 재시도 횟수
    # 'retry_delay': timedelta(minutes=5),  # 재시도 간격
}

# 실패 시 호출될 함수
def on_failure_callback(context):
    # run_slack_alarm(context)  # Slack 알람을 보내는 함수 호출
    return

# DAG 정의
dag = DAG(
    'retry_and_recovery_example',  # DAG 이름
    default_args=default_args,  # 기본 인자 설정
    description='A simple DAG with retry and recovery',  # DAG 설명
    schedule_interval=timedelta(days=1),  # DAG 실행 간격 (매일 실행)
    tags=['example', 'python'],  # DAG 태그
)

# 재시도 및 복구가 필요한 작업 정의
def my_task_function():
    # 예외 발생 시 자동으로 재시도됩니다.
    raise Exception("An error occurred")  # 에러를 발생시켜 재시도 및 복구 기능을 테스트

# PythonOperator를 사용하여 작업 정의
task_with_retry_and_recovery = PythonOperator(
    task_id='task_with_retry_and_recovery',  # 작업 ID
    python_callable=my_task_function,  # 실행할 Python 함수
    retries=3,  # 작업 별 재시도 횟수
    retry_delay=timedelta(seconds=30),  # 작업 별 재시도 간격 (예시 30초)
    # on_failure_callback=on_failure_callback,  # 실패 시 호출될 함수
    dag=dag,  # 이 작업이 속한 DAG
)