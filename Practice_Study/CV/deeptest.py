############
#import는 폴더명에서 가서 __init__.py (생성자영역)을 실행
############
import cv2
import mediapipe as mp

# MediaPipe와 OpenCV 객체 초기화
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0) #비디오중에서 0번은 웹캠

while cap.isOpened():
    ret, frame = cap.read()  # ret는 비디오가 있는가. 비디오의 마지막이 있는가를 확인 가능 #frame은 1/약27
    if ret == False:
        break

    # 이미지 전처리
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_face_mesh.process(frame_rgb)
    print('-'*100)
    print(results.multi_face_landmarks) # 수많은 랜드마크들이 등장한다



