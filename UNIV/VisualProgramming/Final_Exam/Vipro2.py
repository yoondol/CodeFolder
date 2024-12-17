import time

try:
    with open('execution_info.txt', 'r') as file:
        execution_count, total_elapsed_time = map(int, file.read().split())
except FileNotFoundError:
    execution_count = 0
    total_elapsed_time = 0

# 실행 횟수 증가
execution_count += 1

print(f"{execution_count}번째 실행입니다.")

try:
    while True:
        total_elapsed_time += 1
        print(f"{total_elapsed_time}초")
        time.sleep(1)
        with open('execution_info.txt', 'w') as file:
            file.write(f"{execution_count} {total_elapsed_time}")
except KeyboardInterrupt:
    print("프로그램이 강제 종료되었습니다.")
    with open('execution_info.txt', 'w') as file:
        file.write(f"{execution_count} {total_elapsed_time}")