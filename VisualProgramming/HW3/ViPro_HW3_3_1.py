import csv
from datetime import datetime

def load_latest_country_data():
    """모든 국가의 최신 데이터를 로드"""
    country_data = {}
    latest_dates = {}
    
    with open('owid-covid-data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row['location']
            date_str = row['date']
            
            # 빈 데이터 행은 건너뛰기
            if not country or not date_str:
                continue
                
            # 필수 데이터 필드 확인
            required_fields = ['total_cases', 'new_cases', 'total_deaths', 'new_deaths',
                             'total_vaccinations', 'people_vaccinated', 
                             'people_fully_vaccinated', 'total_boosters',
                             'total_cases_per_million', 'total_deaths_per_million',
                             'people_vaccinated_per_hundred', 
                             'people_fully_vaccinated_per_hundred']
            
            # 필수 필드 중 하나라도 비어있으면 건너뛰기
            if any(not row[field] for field in required_fields):
                continue
                
            # 날짜를 datetime 객체로 변환
            current_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # 해당 국가의 최신 데이터 업데이트
            if country not in latest_dates or current_date > latest_dates[country]:
                latest_dates[country] = current_date
                country_data[country] = row
    
    return country_data

def find_similar_countries(search_term, countries):
    #입력된 문자열이 포함된 국가 찾기
    search_term = search_term.lower()
    matches = []
    
    for country in countries:
        if search_term in country.lower():
            matches.append(country)
    
    return matches

def format_number(num_str): #숫자 문자열을 포맷팅
    # 데이터가 비어있을 경우
    if not num_str:
        return "데이터 없음"
    try:
        num = float(num_str)
        # 정수인 경우
        if num.is_integer():
            return f"{int(num):,}"
        # 실수인 경우 천 단위 구분. 소수점 둘째자리까지
        return f"{num:,.2f}"
    # 예외로 원본 반환
    except ValueError:
        return num_str

def display_covid_stats(country_data): #코로나 통계 출력
    if not country_data:
        print("데이터가 없습니다.")
        return

    print("\n== 코로나19 현황 보고서 ==")
    print(f"국가: {country_data['location']}")
    print(f"기준일: {country_data['date']}")
    
    print("\n== 감염 현황 ==")
    print(f"총 확진자: {format_number(country_data['total_cases'])}")
    print(f"신규 확진자: {format_number(country_data['new_cases'])}")
    print(f"총 사망자: {format_number(country_data['total_deaths'])}")
    print(f"신규 사망자: {format_number(country_data['new_deaths'])}")
    
    print("\n== 백신 접종 현황 ==")
    print(f"총 접종 횟수: {format_number(country_data['total_vaccinations'])}")
    print(f"1차 접종자: {format_number(country_data['people_vaccinated'])}")
    print(f"접종 완료자: {format_number(country_data['people_fully_vaccinated'])}")
    print(f"부스터 접종: {format_number(country_data['total_boosters'])}")
    
    print("\n== 인구 대비 통계 ==")
    print(f"백만명당 확진자: {format_number(country_data['total_cases_per_million'])}")
    print(f"백만명당 사망자: {format_number(country_data['total_deaths_per_million'])}")
    print(f"인구 대비 백신 접종률: {format_number(country_data['people_vaccinated_per_hundred'])}%")
    print(f"인구 대비 접종 완료율: {format_number(country_data['people_fully_vaccinated_per_hundred'])}%")

def main():
    # 모든 국가의 최신 데이터 로드
    country_data = load_latest_country_data()
    
    while True:
        search = input("\n국가 이름을 입력하세요 (종료: exit): ").strip()
        
        if search.lower() == 'exit':
            break
        
        # 유사한 국가 찾기
        matches = find_similar_countries(search, country_data.keys())
        
        if not matches:
            print("일치하는 국가를 찾을 수 없습니다.")
            continue
        
        # 하나만 일치
        if len(matches) == 1:
            display_covid_stats(country_data[matches[0]])
        else:
            # 여러 개가 일치
            print("\n다음 중 선택하세요:")
            for i, country in enumerate(matches, 1):
                print(f"{i}. {country}")
            
            while True:
                try:
                    choice = int(input("번호를 선택하세요: "))
                    if 1 <= choice <= len(matches):
                        selected_country = matches[choice-1]
                        display_covid_stats(country_data[selected_country])
                        break
                    print("올바른 번호를 선택하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")

if __name__ == "__main__":
    main()