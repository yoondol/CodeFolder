import cv2
import mediapipe as mp

# MediaPipe 핸드 모듈 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# 핸드 추적 모델 초기화
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# 웹캠 열기
cap = cv2.VideoCapture(0)

while cap.isOpened():
    # 웹캠에서 프레임 읽기
    ret, frame = cap.read()
    
    if not ret:
        print("웹캠 프레임을 읽을 수 없습니다.")
        break

    # BGR 이미지를 RGB로 변환
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 손의 위치 추적
    results = hands.process(rgb_frame)
    
    # 손의 랜드마크를 그리기
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # 결과 프레임을 화면에 표시
    cv2.imshow('MediaPipe Hands', frame)
    
    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 웹캠과 윈도우 자원 해제
cap.release()
cv2.destroyAllWindows()
