from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

'''
push_user_data 태스크:

사용자 정보를 딕셔너리 형태로 생성
XCom에 'user_info'라는 키로 데이터를 저장


pull_and_process_data 태스크:

이전 태스크에서 저장한 데이터를 XCom에서 가져옴
데이터를 처리하고 결과를 출력
'''

# DAG의 기본 인자 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# XCom에 데이터를 push하는 함수
def push_data(**context):
    # 데이터 생성
    data = {
        'name': '홍길동',
        'age': 30,
        'city': '서울'
    }
    # XCom에 데이터 저장
    context['task_instance'].xcom_push(key='user_info', value=data)
    return "데이터 저장 완료"


# XCom에서 데이터를 pull하는 함수
def pull_and_process_data(**context):
    # XCom에서 데이터 가져오기
    user_data = context['task_instance'].xcom_pull(task_ids='push_user_data', key='user_info')

    # 데이터 처리
    processed_message = f"""
    사용자 정보 처리 결과:
    이름: {user_data['name']}
    나이: {user_data['age']}
    도시: {user_data['city']}
    """
    print(processed_message)
    return processed_message


# DAG 정의
dag = DAG(
    'xcom_example',
    default_args=default_args,
    description='XCom을 사용한 태스크 간 데이터 공유 예제',
    schedule_interval='@once',
    tags=['example', 'python', 'xcom'],
)

# 첫 번째 태스크: 데이터를 XCom에 저장
push_task = PythonOperator(
    task_id='push_user_data',
    python_callable=push_data,
    dag=dag,
)

# 두 번째 태스크: XCom에서 데이터를 가져와서 처리
pull_task = PythonOperator(
    task_id='pull_and_process_data',
    python_callable=pull_and_process_data,
    dag=dag,
)

# 태스크 순서 설정
push_task >> pull_task