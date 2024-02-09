from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


BUTTON_MAX_HEIGHT = 40
BUTTON_MAX_WIDTH = 150
LAYOUT_CONTENTS_MARGINS = 5
LAYOUT_CONTENTS_MARGINS_LEFT = LAYOUT_CONTENTS_MARGINS
LAYOUT_CONTENTS_MARGINS_TOP = LAYOUT_CONTENTS_MARGINS
LAYOUT_CONTENTS_MARGINS_RIGHT = LAYOUT_CONTENTS_MARGINS
LAYOUT_CONTENTS_MARGINS_BOTTOM = LAYOUT_CONTENTS_MARGINS

class CompassWidget(QWidget):

    angleChanged = pyqtSignal(float)
    
    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        self._angle = 0.0
        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S",
                           225: "SW", 270: "W", 315: "NW"}
        self.setFixedWidth(150)
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.fillRect(event.rect(), self.palette().brush(QPalette.Window))
        self.drawMarkings(painter)
        self.drawNeedle(painter)
        
        painter.end()
    
    def drawMarkings(self, painter):
    
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        
        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)
        
        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))
        
        i = 0
        while i < 360:
        
            if i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(int(-metrics.width(self._pointText[i])/2.0), -52,
                                 self._pointText[i])
            else:
                painter.drawLine(0, -45, 0, -50)
            
            painter.rotate(15)
            i += 15
        
        painter.restore()
    
    def drawNeedle(self, painter):
    
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(self.palette().brush(QPalette.Shadow))
        
        painter.drawPolygon(
            QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0),
                      QPoint(0, 45), QPoint(-10, 0)])
            )
        
        painter.setBrush(self.palette().brush(QPalette.Highlight))
        
        painter.drawPolygon(
            QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
                      QPoint(0, -30), QPoint(-5, -25)])
            )
        
        painter.restore()
    
    def sizeHint(self):
    
        return QSize(150, 150)
    
    def angle(self):
        return self._angle
    
    # was float
    @pyqtSlot(int)
    def setAngle(self, angle):
    
        if angle != self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()
    
    angle = pyqtProperty(float, angle, setAngle)

class ButtonsVerticalContainers(QVBoxLayout):
    def __init__(self):
        super(ButtonsVerticalContainers, self).__init__()
        self.setContentsMargins(LAYOUT_CONTENTS_MARGINS_LEFT, LAYOUT_CONTENTS_MARGINS_TOP, LAYOUT_CONTENTS_MARGINS_RIGHT, LAYOUT_CONTENTS_MARGINS_BOTTOM)
        
class RovArmedButton(QPushButton):
    def __init__(self):
        super(RovArmedButton, self).__init__()
        self.setText("ROV Disarmed")
        self.setEnabled(False)
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)

class RovSafeModeButton(QPushButton):
    def __init__(self):
        super(RovSafeModeButton, self).__init__()
        self.setText("Safe Mode On")
        self.setEnabled(True)
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)

class MoveArmButton(QPushButton):
    def __init__(self):
        super(MoveArmButton, self).__init__()
        self.setText("Move Arm")
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)


#class to display a small text box with constantly updating values of messages received from the arduino
class DisplayMessageReceivedTextBox(QTextEdit):
    def __init__(self):
        super(DisplayMessageReceivedTextBox, self).__init__()
        self.setPlainText("Initializing...")
        self.setReadOnly(True)
        self.setFixedSize(640, 25)
    def TextUpdateSlot(self, text):
        self.setPlainText(text)