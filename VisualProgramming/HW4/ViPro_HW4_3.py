import pandas as pd
import matplotlib.pyplot as plt

# 한글 글꼴 설정 (Windows)
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 깨짐 방지

# CSV 파일 경로
file_path = "C:/GitCode/CodeFolder/VisualProgramming/HW4/20231231.csv"

# 데이터 읽기
df = pd.read_csv(file_path, encoding='cp949')

# 과목 목록 추출
subjects = df['영역'].unique()

# 과목 선택
print("과목 목록:", subjects)
selected_subject = input("분포를 확인할 과목을 입력하세요: ")

# 선택된 과목 필터링
filtered_df = df[df['영역'] == selected_subject]

# 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(filtered_df['표준점수'], filtered_df['남자'], label='남자', color='blue')
plt.plot(filtered_df['표준점수'], filtered_df['여자'], label='여자', color='orange')

# 그래프 제목 및 축 레이블 설정
plt.title(f"2024학년도 수능 {selected_subject} 과목 분포")
plt.xlabel('표준점수')
plt.ylabel('응시자 수')
plt.legend()

# 그래프 출력
plt.grid()
plt.show()