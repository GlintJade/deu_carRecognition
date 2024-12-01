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
        click_year, click_month, click_day = map(int, self.click_date)

        self.setWindowTitle(f'{click_year}년 {click_month}월 {click_day}일 조회결과')
        self.resize(400, 300)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(2)

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

        self.setGeometry(300, 100, 600, 400)
        self.show()

        # print(f"Click Date: {self.click_date}")

        con = oracledb.connect(user="digital", password="1234", dsn="localhost:1521/XE")
        cursor = con.cursor()

        cursor.execute("select * from LICENSE_TABLE")  # 데이터베이스 명령 실행( cursor가 임시로 보관)
        out_data = cursor.fetchall()  # 커서의 내용을 out_data에 저장
        i = 0
        for row in out_data:
            license_plate, capture_date = row
            date_obj = datetime.strptime(capture_date, "%Y-%m-%d %H:%M:%S.%f")
            year = int(date_obj.year)
            month = int(date_obj.month)
            day = int(date_obj.day)
            time_part = capture_date.split(" ")[1]
            if click_year == year and click_month==month and click_day == day:
                self.tableWidget.setItem(i, 0, QTableWidgetItem(license_plate))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(time_part))
                i += 1


        con.close()

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])
    window = DatabaseGUI()
    window.show()
    app.exec_()