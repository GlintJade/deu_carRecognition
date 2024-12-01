import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
import os
from PIL import Image, ImageDraw
import test as ttt
import oracledb
from itertools import chain
import easyocr
from datetime import datetime



license = []

# 이미지 파일이 있는지 확인하는 함수
def get_image_files(directory):
    # 디렉토리에서 이미지 파일만 가져오기
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg'))]

def find_chars(image):
    ocr_modle = easyocr.Reader(['ko'], gpu=True)
    result = ocr_modle.readtext(image)
    chars = ''

    if len(result) > 0:
        # Step 1: 맨 위 contour를 찾음 (Y축 기준 최소값)
        top_contour = min(result, key=lambda x: min(pt[1] for pt in x[0]))

        # Step 2: 나머지 contour에서 top_contour를 제외하고, X축 기준으로 정렬
        remaining_contours = [contour for contour in result if contour != top_contour]
        sorted_remaining = sorted(remaining_contours, key=lambda x: min(pt[0] for pt in x[0]))

        # Step 3: 최종 contour 순서: 맨 위 contour + 나머지 정렬된 contours
        final_sorted_contours = [top_contour] + sorted_remaining

        image_1 = Image.open(image)
        draw = ImageDraw.Draw(image_1)

        for detection in final_sorted_contours:
            bbox, text, confidence = detection
            print(f"Detected text: {bbox} {text} (Confidence: {confidence:.2f})")
            chars += text

            # 텍스트 영역에 박스 그리기
            draw.polygon([tuple(point) for point in bbox], outline='blue')

        # print(chars)
        return chars.replace(" ", "")
    else:
        print("No text detected.")
        return None


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
            chars = find_chars(image_path)
            if chars:
                license.append((chars, ttt.current_time))
            else:
                print("No characters found. Skipping append.")
            os.remove(image_path)  # 처리 완료된 파일 삭제
            print(f"process_image: {image_path}")
    con = oracledb.connect(user="digital", password="1234", dsn="localhost:1521/XE")
    cursor = con.cursor()

    for chars, time in license:
        print(chars, time)
        cursor.execute(f"insert into LICENSE_TABLE values('{chars}', '{time}')")

    con.commit()
    con.close()

    delete_videos_in_directory(video_directory)



if __name__ == '__main__':
  main()

