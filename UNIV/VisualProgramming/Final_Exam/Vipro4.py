import os
import re

def calculate_expression(expression):
    # 정규식을 사용
    match = re.match(r'(\d+)([+-])(\d+)', expression)
    if match:
        num1, operator, num2 = match.groups()
        num1, num2 = int(num1), int(num2)
        if operator == '+':
            return f"{expression}={num1 + num2}"
        elif operator == '-':
            return f"{expression}={num1 - num2}"
    return expression

current_directory = os.getcwd()

for i in range(1, 10):
    file_name = f"quest{i}.txt"
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as file:
                lines = file.readlines()
            
            # 파일에 기록
            with open(file_name, 'w') as file:
                for line in lines:
                    result = calculate_expression(line.strip())
                    file.write(result + '\n')
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
    else:
        print(f"{file_name} does not exist in the current directory.")