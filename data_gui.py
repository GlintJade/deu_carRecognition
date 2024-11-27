import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon # 아이콘 추가
import main as m
import test as t
# from main_gui import click_date
import oracledb
from datetime import datetime

# main_gui에서 날짜 클릭 -> 확인 버튼 -> database_gui 창 열림
# 창이 열림과 동시에 main_gui의 Date 변수를 통해 database의 날짜와 일치하는 데이터(차량번호) 반환

class DatabaseGUI(QWidget):
    def __init__(self, click_date):
        super().__init__()
        self.click_date = click_date
        self.initUI()

    def initUI(self):
        self.setWindowTitle('조회결과')
        self.resize(400, 300)

        print(f"Click Date: {self.click_date}")
        click_year, click_month, click_day = map(int, self.click_date)
        layout = QVBoxLayout()
        # label = QLabel(f'This is the Database GUI.{click_year},{click_month},{click_day}', self)
        # layout.addWidget(label)
        label = QLabel(f"{click_year}년도 {click_month}년 {click_day}일")
        layout.addWidget(label)

        con = oracledb.connect(user="digital", password="1234", dsn="localhost:1521/XE")
        cursor = con.cursor()

        cursor.execute("select * from LICENSE_TABLE")  # 데이터베이스 명령 실행( cursor가 임시로 보관)
        out_data = cursor.fetchall()  # 커서의 내용을 out_data에 저장
        for row in out_data:
            license_plate, capture_date = row
            date_obj = datetime.strptime(capture_date, "%Y-%m-%d %H:%M:%S.%f")
            year = int(date_obj.year)
            month = int(date_obj.month)
            day = int(date_obj.day)
            if click_year == year and click_month==month and click_day == day:
                label = QLabel(f"license : {license_plate}", self)  # QLabel 생성
                layout.addWidget(label)  # 레이아웃에 추가


        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])
    window = DatabaseGUI()
    window.show()
    app.exec_()