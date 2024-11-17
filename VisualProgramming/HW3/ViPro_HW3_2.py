import random
import time

# 사전 생성
def load_dictionary(file_path):
    dictionary = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            word = line.split(':')[0].strip()  # 단어만 추출
            dictionary.append(word)
    return dictionary

# 단어 랜덤 선택
def get_random_word_by_length(dictionary, length):
    ok_words = [word for word in dictionary if len(word) == length]
    return random.choice(ok_words) if ok_words else None

# 다음 단어 랜덤 선택
def get_next_word(dictionary, length, start_letter):
    ok_words = [word for word in dictionary if len(word) == length and word[0] == start_letter]
    return random.choice(ok_words) if ok_words else None

# 끝말잇기 게임
def word_chain_game(dictionary):
    score = 0
    chances = 3
    stage = 1
    used_words = set()  # 사용한 단어 목록

    print("끝말잇기 게임 시작!")

    while chances > 0:
        print(f"\n[스테이지 {stage}]")
        
        # 4~8글자 길이의 단어 랜덤 제공
        computer_word = get_random_word_by_length(dictionary, random.randint(4, 8))
        print(f"컴퓨터: {computer_word}")
        used_words.add(computer_word)  # 사용 목록에 추가
        
        while True:
            # 사용자 입력
            start_time = time.time()
            user_word = input(f"끝말잇기 단어를 입력하세요 ({len(computer_word)}글자): ").strip()
            elapsed_time = time.time() - start_time

            # 시간 초과 체크
            if elapsed_time > 10:
                print(f"시간 초과! (현재 점수: {score})")
                chances -= 1
                stage += 1
                break

            # 단어 규칙 룰북에 따라 검증
            if (len(user_word) != len(computer_word) or  # 길이 검증
                user_word in used_words or  # 중복 단어 검증
                user_word not in dictionary or  # 사전 존재 유무 검증
                user_word[0] != computer_word[-1]  # 끝말잇기 규칙 검증
            ):
                print(f"틀렸습니다. (현재 점수: {score})")
                chances -= 1
                stage += 1
                break

            # 정답 입력 시
            score += 1
            print(f"맞았습니다! +1점 (현재 점수: {score})")
            used_words.add(user_word)  # 사용 목록에 추가

            # 사용자가 정답시 컴퓨터가 다음 단어 제시
            computer_word = get_next_word(dictionary, len(user_word), user_word[-1])
            if not computer_word:  # 이어지는 단어가 없을 경우
                print("컴퓨터가 졌습니다. 게임 종료!")
                chances = 0
                break
            print(f"컴퓨터: {computer_word}")
            used_words.add(computer_word)  # 사용 목록에 추가
        if chances <= 0:
            break

    print(f"\n게임 종료! 총 점수: {score}")

if __name__ == "__main__":
    file_path = "dict_test_utf8.TXT"
    try:
        dictionary = load_dictionary(file_path)
        word_chain_game(dictionary)
    except FileNotFoundError:
        print(f"파일이 없습니다: {file_path}")
