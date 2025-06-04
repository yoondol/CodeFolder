# 필요한 모듈 및 클래스 import
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# 기본 DAG 설정 및 재시도 관련 설정
default_args = {
    "owner": "airflow",  # DAG 소유자
    "depends_on_past": False,  # 과거 실행 여부에 따라 실행할지 여부
    "start_date": datetime(2025, 6, 1),  # DAG 시작일자
    "email_on_failure": False,  # 실패 시 이메일 알림 여부
    "email_on_retry": False,    # 재시도 시 이메일 알림 여부
    "retries": 1,               # 실패 시 재시도 횟수
    "retry_delay": timedelta(minutes=5),  # 재시도 간격
}

# DAG 정의
dag = DAG(
    "hello_airflow_dag",  # DAG 이름
    default_args=default_args,  
    description="A simple tutorial DAG",  # DAG 설명
    schedule_interval=timedelta(days=1),  # 실행 간격 (매일 1회)
)

# 작업(task)에서 사용할 함수 정의
def print_word(word):
    print(word)

# 작업에 사용할 문장 정의
sentence = "BASE 세션을 멋지게 마쳤으니 ADV 세션도 잘 해봅시다!"

# 문장을 공백으로 나누고, 각 단어마다 작업(task) 생성
prev_task = None
for i, word in enumerate(sentence.split()):
    task = PythonOperator(
        task_id=f"print_word_{i}",  # 고유한 작업 ID
        python_callable=print_word,  # 실행할 함수 지정
        op_kwargs={"word": word},    # 함수에 전달할 인자
        dag=dag,                     # DAG에 작업 추가
    )

    # 이전 작업이 존재하면, 현재 작업이 이전 작업 뒤에 수행되도록 설정
    if prev_task:
        prev_task >> task
    prev_task = task
