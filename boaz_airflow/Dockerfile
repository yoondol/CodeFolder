# Python 이미지 사용
FROM python:3.8-slim

# 환경변수 설정 (Airflow 홈 디렉토리)
ENV AIRFLOW_HOME=/usr/local/airflow

# 필요한 시스템 라이브러리 설치
RUN apt-get update && \
    apt-get install -y gcc libc-dev vim && \
    rm -rf /var/lib/apt/lists/*

# Airflow 설치
RUN pip install apache-airflow

# Airflow 디렉토리 생성 및 초기화
RUN mkdir -p $AIRFLOW_HOME
WORKDIR $AIRFLOW_HOME
RUN airflow db init

# DAG 파일 복사
COPY boaz_airflow_dag.py $AIRFLOW_HOME/dags/

# 포트 노출
EXPOSE 8080

# Airflow 웹서버 및 스케줄러 실행
CMD airflow webserver -p 8080 & airflow scheduler
