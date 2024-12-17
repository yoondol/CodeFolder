sentences = []

while True:
    sentence = input("문장: ")
    if sentence.lower() == 'end':
        break
    sentences.append(sentence)

textset = ''.join(sentences).lower()
textset = textset.replace(' ', '')

# 빈도수 check
char_count = {}
for char in textset:
    if char in char_count:
        char_count[char] += 1
    else:
        char_count[char] = 1

# 정답 찾기
most_common_char = max(char_count, key=char_count.get)
count = char_count[most_common_char]

print(f"최다 문자: '{most_common_char}' (총 {count}회)")