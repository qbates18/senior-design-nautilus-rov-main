# print("Try5: analoggaugewidget.py")
import sys
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPolygon, QPainter, QBrush, QPen
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt

class gaugeWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "PyQt5 Gauge"
        self.top= 150
        self.left= 150
        self.width = 500
        self.height = 500
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 10, Qt.SolidLine))
        painter.drawArc(100, 100, 300, 300, -45 * 16, 270 * 16)

        painter.setPen(QPen(Qt.gray,  5, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        painter.drawEllipse(240, 240, 25, 25)

        painter.setPen(QPen(Qt.gray, 3, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        points = [
            QPoint(250,250),
            QPoint(100,325),
            QPoint(90,320),
            QPoint(95,310)
            ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)


if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = gaugeWidget()
    gui.show()
    sys.exit(App.exec())