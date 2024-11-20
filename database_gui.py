import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon # 아이콘 추가

# main_gui에서 날짜 클릭 -> 확인 버튼 -> database_gui 창 열림
# 창이 열림과 동시에 main_gui의 Date 변수를 통해 database의 날짜와 일치하는 데이터(차량번호) 반환

class DatabaseGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('조회결과')
        self.resize(400, 300)

        layout = QVBoxLayout()
        label = QLabel('This is the Database GUI.', self)
        layout.addWidget(label)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])
    window = DatabaseGUI()
    window.show()
    app.exec_()