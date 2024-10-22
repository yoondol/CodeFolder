# 문장들을 저장할 리스트
sentences = []

# 문장 입력 반복
while True:
    sentence = input("문장: ")
    
    # 'end'를 입력하면 입력 종료
    if sentence.lower() == 'end':
        break
    
    # 입력된 문장을 리스트에 추가
    sentences.append(sentence)

# 모든 문장을 하나의 문자열로 결합하고 소문자로 변환
all_text = ''.join(sentences).lower()

# 공백 제거
all_text = all_text.replace(' ', '')

# 문자 빈도수 계산
char_count = {}
for char in all_text:
    if char in char_count:
        char_count[char] += 1
    else:
        char_count[char] = 1

# 가장 많이 사용된 문자 찾기
most_common_char = max(char_count, key=char_count.get)
count = char_count[most_common_char]

# 결과 출력
print(f"가장 많이 사용된 문자: '{most_common_char}' (총 {count}회)")