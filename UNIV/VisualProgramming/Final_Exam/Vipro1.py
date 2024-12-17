with open('randdict_utf8.TXT', 'r', encoding='utf-8') as file:
    lines = file.readlines()

noun_dict = {}
for line in lines:
    if line.startswith('n.'):
        noun = line[2:].strip()
        first_char = noun[0]
        if first_char in noun_dict:
            noun_dict[first_char].append(noun)
        else:
            noun_dict[first_char] = [noun]


noun_count = {char: len(nouns) for char, nouns in noun_dict.items()} # 첫 글자별 명사 개수 계산

sorted_noun_count = sorted(noun_count.items(), key=lambda x: x[1], reverse=True)[:10]# 가장 많은 것 10개 표시

for char, count in sorted_noun_count:
    print(f"{char}: {count}")