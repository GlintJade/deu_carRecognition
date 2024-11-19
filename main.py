# 실행방법
## 라이브러리 파일들을 설치 - cv2, numpy, matplotlib, pytesseract 등 설치되지 않은 것들 설치하기
## pytesseract 설치방법 : https://pymac.tistory.com/34
## cv2 설치 : https://kali-live.tistory.com/5

# 참고 : https://velog.io/@mactto3487/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-OpenCV-%EC%9E%90%EB%8F%99%EC%B0%A8-%EB%B2%88%ED%98%B8%ED%8C%90-%EC%9D%B8%EC%8B%9D

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
plt.style.use('dark_background')

# 이미지 읽기
img_ori = cv2.imread('car.png')

#이미지 크기 확인
height, width, channel = img_ori.shape
print(height, width, channel)

#이미지 RGB를 Gray로 변환 -> 흑백 사진으로 변환
gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

# 가우시안 블러 - 노이즈 제거 작업
# Thresholding - 흑과 백으로만 사진을 구성 0~255 범위
img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)

img_blur_thresh = cv2.adaptiveThreshold(
    img_blurred,
    maxValue=255.0,
    adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    thresholdType=cv2.THRESH_BINARY_INV,
    blockSize=19,
    C=9
)

plt.figure(figsize=(12,10))
plt.title('Blur and Threshold')
plt.imshow(img_blur_thresh, cmap='gray')
plt.show()


