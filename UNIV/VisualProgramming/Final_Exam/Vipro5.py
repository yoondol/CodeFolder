import matplotlib.pyplot as plt

n = int(input("정수의 개수를 입력하세요 (n<20): "))
numbers = list(map(int, input(f"{n}개의 정수를 입력하세요 (100 이하): ").split()))

labels = [f"{i+1}번" for i in range(n)]
percentages = [f"{(num / sum(numbers)) * 100:.1f}%" for num in numbers]

fig, ax = plt.subplots()
bars = ax.bar(labels, numbers)

for bar, percentage in zip(bars, percentages):
    height = bar.get_height()
    ax.annotate(percentage,
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')

# 그래프 표시
plt.xlabel('항목')
plt.ylabel('값')
plt.title('사용자 입력 데이터 그래프')
plt.show()