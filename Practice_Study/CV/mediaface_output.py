# https://www.assemblyai.com/blog/mediapipe-for-dummies/
import cv2
import mediapipe as mp
import time
import matplotlib.pyplot as plt

#mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=10)
#drawSpec = mpDraw.DrawingSpec(thickness=1, circle_radius=1)

##################################################
# 이미지 읽어오기
# 샘플 이미지를 cv2.imread()로 읽어온다
# Read an image from the specified path.
##################################################
sample_img = cv2.imread('face.png')
plt.figure(figsize = [10, 10]) # 차트 사이즈 잡기
plt.title("Sample Image")
plt.axis('off')  # 차트표시 제거하기
sample_img_rgb=cv2.cvtColor(sample_img, cv2.COLOR_BGR2RGB)   # rGB값 변경, plt.imshow(sample_img[:,:,::-1])
img = sample_img_rgb.copy()  # 원본 보존
# plt.imshow(sample_img_rgb)
# plt.show()



############################################
## face_mash  값 출력
#############################################
face_mesh = mp.solutions.face_mesh
face_detector = face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#drawing = mp.solutions.drawing_utils

results = face_detector.process(img)

################################
## 함수
################################
def drawPoint(bun,img_shape,point):
    h, w, _ = img_shape
    x, y = int(point.x * w), int(point.y * h)
    cv2.circle(img, (x, y), 5, (0, 255, 0), -1)  # 초록색 원 그리기
    cv2.putText(img, str(bun), (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
       


if results.multi_face_landmarks:
    for face_landmarks in results.multi_face_landmarks:
       bunList=[78, 308]  # 왼쪽눈3, 오른쪽눈3개
       pointList=[]
       for bun in bunList:
            point=face_landmarks.landmark[bun]
            pointList.append(point.y*img.shape[1])
            drawPoint(bun,img.shape,point)
resultText=f'y-y : {pointList[0]-pointList[1]}'
cv2.putText(img, resultText, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
print(pointList,resultText)            
plt.imshow(img)
plt.show()