import cv2
import mediapipe as mp
import numpy as np

# Mediapipe 초기화
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose = mp_pose.Pose()
hands = mp_hands.Hands()

def calculate_angle(landmark1, landmark2, landmark3):
    """세 점을 이용해 각도를 계산합니다."""
    vec1 = np.array(landmark1) - np.array(landmark2)
    vec2 = np.array(landmark3) - np.array(landmark2)
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    angle = np.arccos(dot_product / (norm_vec1 * norm_vec2))
    return np.degrees(angle)

# 비디오 캡처
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_pose = pose.process(frame_rgb)
    results_hands = hands.process(frame_rgb)

    if results_pose.pose_landmarks:
        landmarks_pose = results_pose.pose_landmarks.landmark
        elbow1 = landmarks_pose[13]
        elbow2 = landmarks_pose[14]

    if results_hands.multi_hand_landmarks:
        for hand_landmarks in results_hands.multi_hand_landmarks:
            wrist = hand_landmarks.landmark[0]
            middle_finger_mcp = hand_landmarks.landmark[9]

            angle = calculate_angle(
                [elbow1.x, elbow1.y, elbow1.z],
                [wrist.x, wrist.y, wrist.z],
                [middle_finger_mcp.x, middle_finger_mcp.y, middle_finger_mcp.z]
            )
            print(f'Wrist bend angle: {angle:.2f} degrees')

    cv2.imshow('MediaPipe Pose & Hands', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
