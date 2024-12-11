# API 키와 기본 URL 설정
api_key = "32b268d2dba4ce7f9fef781171898229"
base_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"

# 영화 이름 입력 받기
input_movie_name = input("영화명을 입력하세요: ")

# 요청 URL 생성
url = f"{base_url}?key={api_key}&movieNm={input_movie_name}"

# API 요청 수행
response = requests.get(url)

# 응답 데이터 처리
if response.status_code == 200:
    data = response.json()
    
    # 영화 리스트 추출
    movies = data.get('movieListResult', {}).get('movieList', [])
    
    # 입력한 영화 이름과 일치하는 영화 찾기
    if movies:
        for movie in movies:
            print(f"영화명: {movie['movieNm']}, 영어 영화명: {movie['movieNmEn']}")
    else:
        print("영화가 목록에 없습니다.")
else:
    print(f"Error: {response.status_code}")