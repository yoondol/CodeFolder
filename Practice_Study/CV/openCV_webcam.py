import cv2
# cv2.VideoCapture('aaa.mp4')
webcam = cv2.VideoCapture(0) #웹캠

if not webcam.isOpened():
    print('카메라 못찾음')
else:
    print('카메라 활성화 완료')

while webcam.isOpened():
    # ret는 영상물이 진행중인지 확인, frame은 영상에서 들어오는 한장의 사진
    ret, frame = webcam.read() #영상물이라면 마지막일 때는 False가 들어감
    
    # webcam이 활성화되었을 때,
    if ret:
        cv2.imshow('my',frame)
    else:
        cv2.destroyAllWindows()
    
    

# 웹캠은 사용자가 닫음.
webcam.release()
cv2.destroyAllWindows()