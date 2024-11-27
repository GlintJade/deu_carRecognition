# 실행방법
## 라이브러리 파일들을 설치 - cv2, numpy, matplotlib, pytesseract 등 설치되지 않은 것들 설치하기
## pytesseract 설치방법 : https://pymac.tistory.com/34
## cv2 설치 : https://kali-live.tistory.com/5

## 실행 시 IDE - 관리자 권한으로 실행해야 함.

# 참고 : https://velog.io/@mactto3487/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-OpenCV-%EC%9E%90%EB%8F%99%EC%B0%A8-%EB%B2%88%ED%98%B8%ED%8C%90-%EC%9D%B8%EC%8B%9D
# 참고한 깃허브 : https://github.com/Mactto/License_Plate_Recognition/blob/master/opencv.ipynb

# 이미지를 흑백사진으로 변환시켜 흰색 윤곽선을 통해 직사각형으로 나타낸 뒤,
# 번호판 숫자들의 일정한 비율을 통해 글자를 추출하는 방식

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
import os
from PIL import Image
import test as ttt
import oracledb
from itertools import chain

plt.style.use('dark_background')

# 윤곽선 데이터를 필터링하는 작업 -> 조건에 부합하는 윤곽선만 possible_contours에 저장
### 최소 크기를 지정하는 부분이라 너무 작은 번호판을 인식하지 못하는 경우가 발생할 수 있음
MIN_AREA = 80
MIN_WIDTH, MIN_HEIGHT = 2, 8
MIN_RATIO, MAX_RATIO = 0.25, 1.0

MAX_DIAG_MULTIPLYER = 5     # 두 윤곽선 중심 간 거리와 대각선 길이의 비율 허용값
MAX_ANGLE_DIFF = 12.0       # 두 윤곽선 중심 연결선과 수평선 사이의 최대 각도 차이
MAX_AREA_DIFF = 0.5         # 두 윤곽선 면적 차이의 최대 비율
MAX_WIDTH_DIFF = 0.8        # 두 윤곽선 너비 차이의 최대 비율
MAX_HEIGHT_DIFF = 0.2       # 두 윤곽선 높이 차이의 최대 비율
MIN_N_MATCHED = 3           # 유효한 그룹으로 판단이 되는 최소 윤곽선 갯수

PLATE_WIDTH_PADDING = 1.3  # 1.3
PLATE_HEIGHT_PADDING = 1.5  # 1.5
MIN_PLATE_RATIO = 3
MAX_PLATE_RATIO = 10

contours_dict = []
plate_chars = []
possible_contours = []

license_plate_1 = []
license_plate = []
# 이미지 파일이 있는지 확인하는 함수
def get_image_files(directory):
    # 디렉토리에서 이미지 파일만 가져오기
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

# 번호판 contours의 width와 height의 비율, 사이의 간격, 3개 이상 인접한지 ...
# 조건을 충족하는 contours만 추출
def find_chars(contour_list):
    matched_result_idx = []

    for d1 in contour_list:
        matched_contours_idx = []
        for d2 in contour_list:
            if d1['idx'] == d2['idx']:
                continue

            dx = abs(d1['cx'] - d2['cx'])
            dy = abs(d1['cy'] - d2['cy'])

            diagonal_length1 = np.sqrt(d1['w'] ** 2 + d1['h'] ** 2)

            distance = np.linalg.norm(np.array([d1['cx'], d1['cy']]) - np.array([d2['cx'], d2['cy']]))
            if dx == 0:
                angle_diff = 90
            else:
                angle_diff = np.degrees(np.arctan(dy / dx))
            area_diff = abs(d1['w'] * d1['h'] - d2['w'] * d2['h']) / (d1['w'] * d1['h'])
            width_diff = abs(d1['w'] - d2['w']) / d1['w']
            height_diff = abs(d1['h'] - d2['h']) / d1['h']

            # 대각선 길이, 각도, 면적, 너비, 높이 조건을 만족하는 윤곽선을 matched_contours_idx에 1차적으로 넣음
            if distance < diagonal_length1 * MAX_DIAG_MULTIPLYER \
                    and angle_diff < MAX_ANGLE_DIFF and area_diff < MAX_AREA_DIFF \
                    and width_diff < MAX_WIDTH_DIFF and height_diff < MAX_HEIGHT_DIFF:
                matched_contours_idx.append(d2['idx'])

        matched_contours_idx.append(d1['idx'])

        # 윤곽선의 개수가 3개 미만이라면 해당 d1을 건너뛰고 다음 윤곽선으로 실행
        if len(matched_contours_idx) < MIN_N_MATCHED:
            continue

        # 윤곽선의 개수 조건까지 만족하면 최종 변수에 저장
        matched_result_idx.append(matched_contours_idx)

        # 조건을 만족하지 않은 윤곽선 -> find_chars 재귀호출을 통해 조건에 맞는 그룹을 추가 탐색
        # 왜 필요 ? 현재 : 특정 윤곽선(d1)기준 / 다른 윤곽선을 기준으로 하면 다른 유효한 그룹 생길 수 있음 -> 놓친 그룹 찾음
        unmatched_contour_idx = []
        for d4 in contour_list:
            if d4['idx'] not in matched_contours_idx:
                unmatched_contour_idx.append(d4['idx'])

        unmatched_contour = np.take(possible_contours, unmatched_contour_idx)

        recursive_contour_list = find_chars(unmatched_contour)

        for idx in recursive_contour_list:
            matched_result_idx.append(idx)

        break # 한 번의 루프에서 하나의 그룹만 처리하기

    return matched_result_idx


# 이미지 파일을 처리하는 함수
def process_image(image_path):
    try:
        print(f"Processing: {image_path}")
        # 이미지 열기 (예시로 PIL 사용)
        with (Image.open(image_path) as img):
            # 이미지 크기 확인

            img_ori = cv2.imread(image_path)
            height, width, channel = img_ori.shape
            print(height, width, channel)

            # 이미지 RGB를 Gray로 변환 -> 흑백 사진으로 변환
            gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

            # 가우시안 블러 - 노이즈 제거 작업
            # Thresholding - 흑과 백으로만 사진을 구성 0~255 범위
            img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)

            # # Thresholding - 흑과 백으로만 사진을 구성 0(검은색 픽셀), 255(흰색 픽셀)로 구성
            img_thresh = cv2.adaptiveThreshold(  # 가우시안 블러 적용 X
                gray,
                maxValue=255.0,
                adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                thresholdType=cv2.THRESH_BINARY_INV,
                blockSize=19,
                C=9
            )

            img_blur_thresh = cv2.adaptiveThreshold(  # 가우시안 블러 적용 O
                img_blurred,
                maxValue=255.0,
                adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                thresholdType=cv2.THRESH_BINARY_INV,
                blockSize=19,
                C=9
            )

            # 경계선 찾기, 검은색 바탕에서 흰색 대상 찾음
            contours, _ = cv2.findContours(
                img_blur_thresh,
                mode=cv2.RETR_LIST,
                method=cv2.CHAIN_APPROX_SIMPLE
            )

            # 0으로 채워진 배열 생성 -> temp_result는 검은색으로 채워진 이미지
            temp_result = np.zeros((height, width, channel), dtype=np.uint8)



            # 윤곽선 정보가 담긴 contours에서 x, y, width, height를 통해 흰색 직사각형을 그리는 작업
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(temp_result, pt1=(x, y), pt2=(x + w, y + h), color=(255, 255, 255), thickness=2)

                contours_dict.append({
                    'contour': contour,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h,
                    'cx': x + (w / 2),  # 중심점
                    'cy': y + (h / 2)
                })



            cnt = 0
            for d in contours_dict:
                area = d['w'] * d['h']
                ratio = d['w'] / d['h']

                if area > MIN_AREA \
                        and d['w'] > MIN_WIDTH and d['h'] > MIN_HEIGHT \
                        and MIN_RATIO < ratio < MAX_RATIO:
                    d['idx'] = cnt  # 윤곽선에 인덱스를 부여 -> 추후 작업에 참조
                    cnt += 1
                    possible_contours.append(d)
            # 크기와 비율 조건을 만족했던 possible_contours를 find_chars에 해당하는 조건을 만족하는 contours 추리기
            result_idx = find_chars(possible_contours)
            matched_result = []
            for idx_list in result_idx:
                matched_result.append(np.take(possible_contours, idx_list))

            temp_result = np.zeros((height, width, channel), dtype=np.uint8)

            # 조건을 만족하는 그룹별 윤곽선이 흰색 직사각형으로
            for r in matched_result:
                for d in r:
                    cv2.rectangle(temp_result, pt1=(d['x'], d['y']), pt2=(d['x'] + d['w'], d['y'] + d['h']),
                                  color=(255, 255, 255),
                                  thickness=2)
            plate_imgs = []
            plate_infos = []

            for i, matched_chars in enumerate(matched_result):
                sorted_chars = sorted(matched_chars, key=lambda x: x['cx'])

                plate_cx = (sorted_chars[0]['cx'] + sorted_chars[-1]['cx']) / 2
                plate_cy = (sorted_chars[0]['cy'] + sorted_chars[-1]['cy']) / 2

                plate_width = (sorted_chars[-1]['x'] + sorted_chars[-1]['w'] - sorted_chars[0][
                    'x']) * PLATE_WIDTH_PADDING

                sum_height = 0
                for d in sorted_chars:
                    sum_height += d['h']

                plate_height = int(sum_height / len(sorted_chars) * PLATE_HEIGHT_PADDING)

                triangle_height = sorted_chars[-1]['cy'] - sorted_chars[0]['cy']
                triangle_hypotenus = np.linalg.norm(
                    np.array([sorted_chars[0]['cx'], sorted_chars[0]['cy']]) -
                    np.array([sorted_chars[-1]['cx'], sorted_chars[-1]['cy']])
                )

                angle = np.degrees(np.arcsin(triangle_height / triangle_hypotenus))

                rotation_matrix = cv2.getRotationMatrix2D(center=(plate_cx, plate_cy), angle=angle, scale=1.0)

                img_rotated = cv2.warpAffine(img_thresh, M=rotation_matrix, dsize=(width, height))

                img_cropped = cv2.getRectSubPix(
                    img_rotated,
                    patchSize=(int(plate_width), int(plate_height)),
                    center=(int(plate_cx), int(plate_cy))
                )

                if img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO or img_cropped.shape[1] / \
                        img_cropped.shape[
                            0] < MIN_PLATE_RATIO > MAX_PLATE_RATIO:
                    continue

                plate_imgs.append(img_cropped)
                plate_infos.append({
                    'x': int(plate_cx - plate_width / 2),
                    'y': int(plate_cy - plate_height / 2),
                    'w': int(plate_width),
                    'h': int(plate_height)
                })

                longest_idx, longest_text = -1, 0


                for i, plate_img in enumerate(plate_imgs):
                    plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.6, fy=1.6)
                    _, plate_img = cv2.threshold(plate_img, thresh=0.0, maxval=255.0,
                                                 type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)

                    # find contours again (same as above)
                    contours, _ = cv2.findContours(plate_img, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

                    plate_min_x, plate_min_y = plate_img.shape[1], plate_img.shape[0]
                    plate_max_x, plate_max_y = 0, 0

                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)

                        area = w * h
                        ratio = w / h

                        if area > MIN_AREA \
                                and w > MIN_WIDTH and h > MIN_HEIGHT \
                                and MIN_RATIO < ratio < MAX_RATIO:
                            if x < plate_min_x:
                                plate_min_x = x
                            if y < plate_min_y:
                                plate_min_y = y
                            if x + w > plate_max_x:
                                plate_max_x = x + w
                            if y + h > plate_max_y:
                                plate_max_y = y + h

                    img_result = plate_img[plate_min_y:plate_max_y, plate_min_x:plate_max_x]

                img_result = cv2.GaussianBlur(img_result, ksize=(3, 3), sigmaX=0)
                _, img_result = cv2.threshold(img_result, thresh=0.0, maxval=255.0,
                                              type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                img_result = cv2.copyMakeBorder(img_result, top=10, bottom=10, left=10, right=10,
                                                borderType=cv2.BORDER_CONSTANT,
                                                value=(0, 0, 0))

                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                chars = pytesseract.image_to_string(img_result, lang='kor', config='--psm 7 --oem 3')

                result_chars = ''
                has_digit = False
                for c in chars:
                    if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
                        if c.isdigit():
                            has_digit = True
                        result_chars += c

                # print(result_chars)
                plate_chars.append(result_chars)

                if has_digit and len(result_chars) > longest_text:
                    longest_idx = i

                info = plate_infos[longest_idx]
                chars = plate_chars[longest_idx]

                print(chars)
                license_plate_1.append(chars)
                img_out = img_ori.copy()

                cv2.rectangle(img_out, pt1=(info['x'], info['y']), pt2=(info['x'] + info['w'], info['y'] + info['h']),
                              color=(255, 0, 0), thickness=2)

                # cv2.imwrite(chars + '.jpg', img_out)

                plt.figure(figsize=(12, 10))
                plt.imshow(img_out)
                plt.show()
        return chars

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")


def delete_videos_in_directory(directory):
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return

    # 비디오 파일 확장자 목록 (필요시 추가 가능)
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')

    # 디렉토리 내 파일 확인
    files = os.listdir(directory)
    if not files:
        print(f"No files in directory: {directory}")
        return

    for file_name in files:
        file_path = os.path.join(directory, file_name)

        # 파일인지 확인하고 비디오 파일만 삭제
        if os.path.isfile(file_path) and file_name.lower().endswith(video_extensions):
            os.remove(file_path)
            print(f"Deleted video file: {file_path}")
        else:
            print(f"Skipped: {file_path}")

    print("All video files in the directory have been processed.")



# 메인 루프
def main():
    directory = './cropped_captures'
    video_directory = "./video"
    while True:
        image_files = get_image_files(directory)
        if not image_files:
            print("No more images to process. Exiting.")
            break

        for image_path in image_files:
            image_path = image_path.replace("\\", "/")
            print(f"read_file: {image_path}")
            license_plate_1.append(process_image(image_path))
            os.remove(image_path)  # 처리 완료된 파일 삭제
            print(f"process_image: {image_path}")
    delete_videos_in_directory(video_directory)

    con = oracledb.connect(user="digital", password="1234", dsn="localhost:1521/XE")
    cursor = con.cursor()

    license_plate.append(list(set(license_plate_1)))
    license_plate_2 = list(chain.from_iterable(license_plate))

    for plate in license_plate_2:
        if plate is not None:  # None이 아니고 문자열인지 확인
            ttt.current_time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f"insert into LICENSE_TABLE values('{plate}', '{ttt.current_time}')")

    con.commit()
    con.close()




    # chars # 번호판 출력
    # ttt.current_time #번호판 이미지 추출한 시간 가져옴
if __name__ == '__main__':
  main()

  print(f"{license_plate}") # 번호판 출력
