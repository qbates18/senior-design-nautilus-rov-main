# print("Try5: analoggaugewidget.py")
import sys
import math
from PyQt5.QtGui import *
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

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
        self._angle = 150.0
        self.InitWindow()
        self._margins = 10

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.drawCircleGauge(painter)
        self.drawColor(painter)
        self.drawNeedle(painter)
        self.drawMarkings(painter)
        
        painter.end()

    def drawNeedle(self, painter):

        painter.save()
        painter.setPen(QPen(Qt.gray,  5, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
        painter.drawEllipse(237, 237, 25, 25)

        painter.translate(self.width/2, self.height/2)
        painter.rotate(self._angle)

        painter.setPen(QPen(Qt.gray, 5, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        points = [
            QPoint(0,0),
            QPoint(-130,130),
            ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)

        painter.restore()

    def drawCircleGauge(self, painter):
        painter.save()
        painter.setPen(QPen(Qt.black, 10, Qt.SolidLine))
        painter.drawArc(100, 100, 300, 300, -45 * 16, 270 * 16)

        painter.restore()

    def drawColor(self, painter):
        painter.save()

        painter.setPen(QPen(Qt.green, 7, Qt.SolidLine))
        painter.drawArc(90, 90, 320, 320, 10 * 16, 215 * 16)

        painter.setPen(QPen(Qt.red, 7, Qt.SolidLine))
        painter.drawArc(90, 90, 320, 320, -45 * 16, 58 * 16)

        painter.restore()

    def drawMarkings(self, painter):
        
        painter.save()
        painter.translate(self.width/2, self.height/2)
        painter.setPen(QPen(Qt.gray, 3, Qt.SolidLine))

        i = 0
        
        while i < 285:
        
            if i % 45 == 0:
                painter.drawLine(-100, 100, -125, 125)
            else:
                painter.drawLine(-100, 100, -125, 125)
            
            painter.rotate(15)
            i += 15
        
        painter.restore()
    
    def angle(self):
        return self._angle

    @pyqtSlot(int)
    def setAngle(self, angle):
    
        if angle != self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()
    

if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = gaugeWidget()
    gui.show()
    sys.exit(App.exec())