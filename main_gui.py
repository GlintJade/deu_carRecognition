import main as m
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon # 아이콘 추가
from PyQt5.QtCore import QCoreApplication, QDate, QSize
from database_gui import DatabaseGUI as db


class MyApp(QWidget):

  def __init__(self):
      super().__init__()
      self.initUI()

  def initUI(self):
      # 확인 버튼
      # self.dialog = QDialog()
      btn = QPushButton('확인', self)
      btn.move(670, 530)
      btn.setFixedSize(120, 40)
      btn.clicked.connect(self.open_database_gui)

      # 레이아웃을 특정 영역에만 적용 -> 이유 : btn버튼을 widget에 넣으면 위치 조정 불가능,
      # btn 버튼을 위젯에 넣어야만 클릭이 되는 오류 발생 / 이유 : self.setLayer때문
      # 해결 : container(영역)을 지정하여 영역 안에 특정 위젯만 넣음 (달력, 레이블)
      container = QWidget(self)  # 컨테이너 위젯 생성
      container.setGeometry(0, 0, 800, 500)  # 컨테이너의 위치와 크기 설정


      # 달력 생성
      cal = QCalendarWidget(container)
      cal.setGridVisible(False)
      cal.setFixedSize(QSize(780, 500))
      cal.clicked[QDate].connect(self.showDate)

      # 레이블 필요없는데 일단 확인용 -> 나중에 삭제
      self.lbl = QLabel(container)
      date = cal.selectedDate()     # 클릭한 날짜가 저장된 변수 -> 가공해서 DB와 연결
      self.lbl.setText(date.toString())

      layout = QVBoxLayout()
      layout.addWidget(cal)
      layout.addWidget(self.lbl)

      container.setLayout(layout)


      # 창 꾸미기
      self.setWindowTitle('불법주정차 리스트')
      self.setWindowIcon(QIcon('warning.png'))      #주제에 맞는 아이콘 추천점..
      self.center()
      self.resize(800,600)
      self.show()

  def open_database_gui(self):
      if not hasattr(self, 'database_window') or not self.database_window.isVisible():
          self.database_window = db()
          self.database_window.show()

  def showDate(self, date):
      self.lbl.setText(date.toString())

  def center(self):
      qr = self.frameGeometry()
      cp = QDesktopWidget().availableGeometry().center()
      qr.moveCenter(cp)
      self.move(qr.topLeft())


if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MyApp()
  sys.exit(app.exec_())