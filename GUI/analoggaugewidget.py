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
        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S",
                           225: "SW", 270: "W", 315: "NW"}

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
        painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
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

        self.drawMarkings(painter)
        
        painter.end()

    def drawMarkings(self, painter):
    
        font = QFont(self.font())
        font.setPixelSize(50)
        metrics = QFontMetricsF(font)
        
        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))
        
        i = 0
        while i < 360:
        
            if i % 45 == 0:
                painter.drawLine(150, 140, 110, 150)
                painter.drawText(int(-metrics.width(self._pointText[i])/2.0), -52,
                                 self._pointText[i])
            else:
                painter.drawLine(150, 145, 110, 150)
            
            painter.rotate(15)
            i += 15
        
        painter.restore()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = gaugeWidget()
    gui.show()
    sys.exit(App.exec())