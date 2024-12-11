FROM apache/airflow:2.8.2

# 모든 pip 설치를 한 번의 RUN 명령어로 통합
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ENV PIP_USER=false
# 가상환경 생성 (필요 시)

ENV PIP_USER=true