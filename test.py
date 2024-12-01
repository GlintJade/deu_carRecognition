import torch
import cv2
import os
from pathlib import Path
import sys
import pathlib
from datetime import datetime




temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

sys.path.insert(0, './model')

# 모델 로드
model = torch.hub.load('./yolov5', 'custom', path='./model/best.pt', source='local')

# 동영상 파일 경로
video_path = 'video/car_1.mp4'

# 결과 저장 디렉토리
output_dir = "./captures"
cropoutput_dir = "./cropped_captures"
os.makedirs(output_dir, exist_ok=True)

# 비디오 캡처 객체 생성
cap = cv2.VideoCapture(video_path)

frame_count = 0
capture_count = 0
CONFIDENCE_THRESHOLD = 0.6  # 신뢰도 기준 설정
FRAME_INTERVAL = 10  # 프레임 간격 설정 (10 프레임마다 처리)

# 번호판 탐지 결과 저장 리스트
detections_list = []

# 동영상 프레임 처리
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("동영상 끝 또는 읽기 실패.")
        break

    frame_count += 1

    # 프레임 간격 조건
    if frame_count % FRAME_INTERVAL != 0:
        continue

    # YOLO 모델로 프레임 추론
    results = model(frame)

    # 탐지된 객체를 DataFrame 형식으로 가져오기
    detections = results.pandas().xyxy[0]

    # 번호판("licence")와 Confidence 기준 필터링
    licence_detections = detections[(detections['name'] == 'licence') & (detections['confidence'] >= CONFIDENCE_THRESHOLD)]

    for _, licence in licence_detections.iterrows():
        x1, y1, x2, y2 = int(licence['xmin']), int(licence['ymin']), int(licence['xmax']), int(licence['ymax'])
        confidence = licence['confidence']
        cropped_image = frame[y1:y2, x1:x2]
        detections_list.append({'confidence': confidence, 'cropped_image': cropped_image})


        # 번호판 영역에 사각형 그리기
        x1, y1, x2, y2 = int(licence['xmin']), int(licence['ymin']), int(licence['xmax']), int(licence['ymax'])
        confidence = licence['confidence']

        # 사각형 그리기
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 초록색 박스

        # 신뢰도 텍스트 추가
        label = f"{confidence:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cap.release()

    if detections_list:
        best_detection = max(detections_list, key=lambda x: x['confidence'])
        best_cropped_image = best_detection['cropped_image']
        best_confidence = best_detection['confidence']

        # 저장
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        cropped_path = os.path.join(cropoutput_dir, f"best_cropped_{current_time}.jpg")
        cv2.imwrite(cropped_path, best_cropped_image)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"가장 신뢰도 높은 번호판 저장: {cropped_path} (신뢰도: {best_confidence:.2f})")
    else:
        print("탐지된 번호판이 없습니다.")

cap.release()

