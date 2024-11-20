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
      btn.move(695, 550)
      btn.setFixedSize(120, 40)
      btn.clicked.connect(self.open_database_gui)

      # btn.clicked.connect(QCoreApplication.instance().quit)

      # 달력 생성
      cal = QCalendarWidget(self)
      cal.setGridVisible(False)
      cal.setFixedSize(QSize(800, 500))
      cal.clicked[QDate].connect(self.showDate)
      self.lbl = QLabel(self)
      date = cal.selectedDate()     # 클릭한 날짜가 저장된 변수 -> 가공해서 DB와 연결
      self.lbl.setText(date.toString())

      layout = QVBoxLayout()
      layout.addWidget(cal)
      layout.addWidget(btn)
      layout.addWidget(self.lbl)

      self.setLayout(layout)


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