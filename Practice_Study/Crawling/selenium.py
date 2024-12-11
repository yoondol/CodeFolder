#step1.selenium 패키지와 time 모듈 import
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

#step2.검색할 키워드 입력
#query = input('검색할 키워드를 입력하세요: ')
query = '장마'
#step3.크롬드라이버로 원하는 url로 접속
url = 'https://www.naver.com/'
driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)
#step4.검색창에 키워드 입력 후 엔터
search_box = driver.find_element(By.ID, "query")
search_box.send_keys(query)
search_box.send_keys(Keys.RETURN)
time.sleep(2)
#step5.뉴스 탭 클릭
#driver.find_element_by_xpath('//*[@id="lnb"]/div[1]/div/ul/li[2]/a').click()
#driver.find_element_by_xpath('//*[@id="lnb"]/div[1]/div/div[1]/div/div[1]/div[1]/a').click()
driver.find_element(By.XPATH,'//*[@id="lnb"]/div[1]/div/div[1]/div/div[1]/div[1]/a').click()
time.sleep(20)