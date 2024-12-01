import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QDate, QSize
from datetime import datetime
import main as m

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.click_date = []  # 클래스 변수로 click_date 선언
        self.initUI()

    def initUI(self):
        # 확인 버튼
        btn = QPushButton('확인', self)
        btn.move(670, 530)
        btn.setFixedSize(120, 40)
        btn.clicked.connect(self.open_database_gui)  # 클릭 이벤트 연결

        # 컨테이너 생성
        container = QWidget(self)
        container.setGeometry(0, 0, 800, 500)

        # 달력 생성
        self.cal = QCalendarWidget(container)
        self.cal.setGridVisible(False)
        self.cal.setFixedSize(QSize(780, 500))
        self.cal.clicked[QDate].connect(self.showDate)

        # 레이블 생성
        self.lbl = QLabel(container)
        date = self.cal.selectedDate()
        self.lbl.setText(date.toString())

        # 기본 날짜 설정
        self.update_click_date(date)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.cal)
        layout.addWidget(self.lbl)
        container.setLayout(layout)




        # 창 꾸미기
        self.setWindowTitle('불법주정차 리스트')
        self.setWindowIcon(QIcon('warning.jpg'))
        self.center()
        self.resize(800, 600)
        self.show()

    def update_click_date(self, date):
        """선택된 날짜를 click_date에 업데이트"""
        formatted_date = date.toString("yyyy MM dd")
        year, month, day = formatted_date.split(" ")
        self.click_date = [year, month, day]

    def open_database_gui(self):
        """DatabaseGUI 창 열기"""
        from data_gui import DatabaseGUI
        if not hasattr(self, 'database_window') or not self.database_window.isVisible():
            self.database_window = DatabaseGUI(self.click_date)  # click_date 전달
            self.database_window.show()

    def showDate(self, date):
        """날짜 클릭 시 업데이트 및 레이블 표시"""
        self.lbl.setText(date.toString())
        self.update_click_date(date)

    def center(self):
        """창을 화면 중앙에 배치"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def on_main_completed():
    # GUI 실행
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    m.main()
    on_main_completed()
