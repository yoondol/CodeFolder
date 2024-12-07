import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy.stats import gaussian_kde
import numpy as np

# 한글 폰트 설정
rc('font', family='Malgun Gothic')  # Windows
plt.rcParams['axes.unicode_minus'] = False  # 음수 깨짐 방지

# 데이터 읽기 함수
def load_data(file_path):
    return pd.read_csv(file_path, encoding='cp949')

# 밀도 추정을 사용한 그래프 그리기
def plot_distribution_with_kde(data):
    # 필요한 데이터 추출
    score = data["표준점수"]
    male = data["남자"]
    female = data["여자"]

    # 데이터 준비
    male_kde = gaussian_kde(np.repeat(score, male))
    female_kde = gaussian_kde(np.repeat(score, female))

    # X축 범위 설정
    x_vals = np.linspace(score.min(), score.max(), 500)

    # 그래프 그리기
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, male_kde(x_vals), label="남자", color='blue', linewidth=2)
    plt.plot(x_vals, female_kde(x_vals), label="여자", color='orange', linewidth=2)

    # 그래프 제목 및 라벨 설정
    plt.title("2024학년도 수능 국어 과목 분포", fontsize=16)
    plt.xlabel("표준점수", fontsize=12)
    plt.ylabel("밀도", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

    # 그래프 출력
    plt.show()

# 메인 실행 코드
if __name__ == "__main__":
    file_path = "C:/GitCode/CodeFolder/VisualProgramming/HW4/20231231.csv"  # 파일 경로 수정
    data = load_data(file_path)  # 데이터 읽기
    plot_distribution_with_kde(data)  # 밀도 기반 그래프 그리기
