
import pandas as pd
from bs4 import BeautifulSoup
import requests
for num in range(1,38):
    url=f'https://opendata.hira.or.kr/op/opc/olapHthInsRvStatInfoTab1.do?docNo=03-{num:03}'
    print(url)

    r = requests.get(url)
    soup = BeautifulSoup(r.text,"lxml")
    df_list = pd.read_html(url, encoding='utf-8')
    print(len(df_list))
    df=df_list[0]
    df.to_csv(f'03-{num}.csv', encoding='euc-kr', index=False )
    print(f'{num} ----> end')