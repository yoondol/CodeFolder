
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request

url='http://apis.data.go.kr/1741000/TsunamiShelter4/getTsunamiShelter4List?serviceKey=QI%2FeHlXdid4qzbUB5UZsXoKwc6dYeFTvwU7sJLExhigSfgpzZwrgPhPMDwEXAt6%2BIRpi9UysYmF%2BmShhsdYfXg%3D%3D&pageNo=1&numOfRows=10&type=xml'
response=urllib.request.urlopen(url)
html_doc=response.read()
soup=BeautifulSoup(html_doc,'xml') 

datas=soup.find_all('row')
dataList=[]
for data in datas:
    sido=data.find('sido_name').string
    sigun=data.find('sigungu_name').string
    div=data.find('shel_div_type').string
    x={'시도':sido,
       'sigun':sigun,
       '장소구분':div}
    dataList.append(x)
df=pd.DataFrame(dataList)
print(df)
