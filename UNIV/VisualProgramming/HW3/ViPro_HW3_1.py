def load_dictionary(file_path):
    dictionary = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if ':' in line:  # ':' 구분 확인
                word, meaning = line.strip().split(':', 1)
                dictionary[word.strip()] = meaning.strip()
    return dictionary

def search_word(dictionary):
    while True:
        word = input("word? (종료하려면'exit'): ").strip()
        if word.lower() == 'exit':
            print("종료합니다.")
            break
        meaning = dictionary.get(word)
        if meaning:
            print(f"{word} : {meaning}")
        else:
            print(f"'{word}'가 사전에 없습니다.")

if __name__ == "__main__":
    file_path = "dict_test_utf8.TXT"  # 파일 불러오기
    print("사전을 만드는 중")
    try:
        eng_kor_dict = load_dictionary(file_path)
        print("사전 제작 성공.")
        search_word(eng_kor_dict)
    except FileNotFoundError:
        print(f"파일이 없습니다: {file_path}")
