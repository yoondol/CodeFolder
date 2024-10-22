target_numbers = []

for num in range(100, 1000):
    # 각 자리 숫자
    hundred = num // 100
    ten = (num % 100) // 10
    unit = num % 10
    three_squared = hundred**3 + ten**3 + unit**3
    if three_squared == num:
        target_numbers.append(num)

print(target_numbers)