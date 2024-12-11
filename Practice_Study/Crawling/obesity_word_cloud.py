import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CSV 파일 읽기
path = 'NewsResult_20240412-20240712.xlsx'

# 2. 데이터프레임 읽기
df = pd.read_excel(path)
print(df.info())
field = '특성추출(가중치순 상위 50개)'
# field = '키워드'



# # 3. 워드클라우드 생성
# # 한글 폰트 설정
df ['키워드'] = df['키워드'].str.replace(',',' ')
df = df[df['언론사'] == '한국일보'].copy()
text = ' '.join(df[field].dropna().astype(str))
font_path = 'malgun.ttf'

# # 워드클라우드 객체 생성
wordcloud = WordCloud(font_path=font_path, background_color='white', width=800, height=600).generate(text)

# # 4. 워드클라우드 시각화
plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
