import numpy as np
import glob
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# 파일 읽기
def load_data():
    pressure_files = glob.glob('data_pressure_*.npy')
    no_pressure_files = glob.glob('data_no_pressure_*.npy')

    pressure_data = []
    no_pressure_data = []

    for file in pressure_files:
        pressure_data.append(np.load(file))
    for file in no_pressure_files:
        no_pressure_data.append(np.load(file))

    pressure_data = np.concatenate(pressure_data)
    no_pressure_data = np.concatenate(no_pressure_data)

    return pressure_data, no_pressure_data

# 데이터 로드
pressure_data, no_pressure_data = load_data()

# 레이블 추가
pressure_labels = np.ones(pressure_data.shape[0])
no_pressure_labels = np.zeros(no_pressure_data.shape[0])

# 데이터와 레이블 결합
X = np.concatenate((pressure_data, no_pressure_data))
y = np.concatenate((pressure_labels, no_pressure_labels))

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 데이터 표준화
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train.reshape(-1, 1))
X_test = scaler.transform(X_test.reshape(-1, 1))

# 모델 학습
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 모델 평가
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))
