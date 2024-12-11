import cv2
import mediapipe as mp
import numpy as np

# MediaPipe 초기화
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
hands = mp_hands.Hands()
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 벡터 간의 각도 계산 함수
def calculate_angle(a, b):
    a = np.array(a)
    b = np.array(b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    angle = np.arccos(dot_product / (norm_a * norm_b))
    return np.degrees(angle)  # 결과를 도 단위로 변환

# 카메라 캡처
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 이미지 처리
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # MediaPipe Pose 처리
    pose_results = pose.process(frame_rgb)
    
    # MediaPipe Hands 처리
    hands_results = hands.process(frame_rgb)

    if pose_results.pose_landmarks and hands_results.multi_hand_landmarks:
        for hand_landmarks in hands_results.multi_hand_landmarks:
            # 손목과 가운데 손가락 뼈 랜드마크 추출
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            wrist_pos = np.array([wrist.x, wrist.y, wrist.z])
            middle_finger_tip_pos = np.array([middle_finger_tip.x, middle_finger_tip.y, middle_finger_tip.z])

            # MediaPipe Pose에서 왼쪽 팔꿈치 랜드마크 추출
            if pose_results.pose_landmarks:
                left_elbow = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
                left_elbow_pos = np.array([left_elbow.x, left_elbow.y, left_elbow.z])

                # 벡터 정의
                vector_wrist_to_left_elbow = left_elbow_pos - wrist_pos
                vector_wrist_to_middle_finger = middle_finger_tip_pos - wrist_pos

                # 각도 계산
                angle = calculate_angle(vector_wrist_to_left_elbow, vector_wrist_to_middle_finger)
                print(f"Wrist Flexion Angle: {angle:.2f} degrees")

                # 손목과 가운데 손가락 뼈, 왼쪽 팔꿈치 랜드마크만 그리기
                # draw_landmarks에 랜드마크 리스트를 제공하기 위한 조치
                hand_landmarks_list = [hand_landmarks]
                for hand in hand_landmarks_list:
                    mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                if pose_results.pose_landmarks:
                    mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # 개별 랜드마크 그리기
                # 손목
                wrist_pos = (int(wrist.x * frame.shape[1]), int(wrist.y * frame.shape[0]))
                cv2.circle(frame, wrist_pos, 5, (0, 255, 0), -1)
                # 가운데 손가락 끝
                middle_finger_tip_pos = (int(middle_finger_tip.x * frame.shape[1]), int(middle_finger_tip.y * frame.shape[0]))
                cv2.circle(frame, middle_finger_tip_pos, 5, (255, 0, 0), -1)
                # 왼쪽 팔꿈치
                left_elbow_pos = (int(left_elbow.x * frame.shape[1]), int(left_elbow.y * frame.shape[0]))
                cv2.circle(frame, left_elbow_pos, 5, (0, 0, 255), -1)

    cv2.imshow('MediaPipe Hands and Pose', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
