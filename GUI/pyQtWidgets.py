from PyQt5.QtGui import *
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
from imports import timeDeploymentStarted
from imports import RotationCounter

BUTTON_MAX_HEIGHT = 40
BUTTON_MAX_WIDTH = 200
BUTTON_MIN_WIDTH = 175
GREEN_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(30, 255, 30, 60%);"
ORANGE_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(255, 175, 5, 60%);"
RED_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(255, 30, 30, 60%);"
BLUE_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(75, 150, 255, 60%)"
GREY_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(128, 128, 128, 60%)"
SMALL_TEXT_BOX_MAX_WIDTH = 40
COMPASS_FIXED_WIDTH = 200
COMPASS_FIXED_HEIGHT = 200
INDICATOR_FIXED_HEIGHT = 50
INDICATOR_MIN_WIDTH = 80
PILOT_LOG_MIN_HEIGHT = 50
PILOT_LOG_MIN_WIDTH = 50
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
        self.setFixedWidth(COMPASS_FIXED_WIDTH)
        self.setFixedHeight(COMPASS_FIXED_HEIGHT)
    
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
    
        return QSize(COMPASS_FIXED_WIDTH, COMPASS_FIXED_HEIGHT)
    
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

class VerticalContainer(QVBoxLayout):
    def __init__(self):
        super(VerticalContainer, self).__init__()
        self.setContentsMargins(LAYOUT_CONTENTS_MARGINS_LEFT, LAYOUT_CONTENTS_MARGINS_TOP, LAYOUT_CONTENTS_MARGINS_RIGHT, LAYOUT_CONTENTS_MARGINS_BOTTOM)

class HorizontalContainer(QHBoxLayout):
    def __init__(self):
        super(HorizontalContainer, self).__init__()
        self.setContentsMargins(LAYOUT_CONTENTS_MARGINS_LEFT, LAYOUT_CONTENTS_MARGINS_TOP, LAYOUT_CONTENTS_MARGINS_RIGHT, LAYOUT_CONTENTS_MARGINS_BOTTOM)
        
class RovArmedButton(QPushButton):
    def __init__(self):
        super(RovArmedButton, self).__init__()
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)
        self.setText("ROV Disarmed")
        self.setStyleSheet(GREEN_BUTTON_BACKGROUND_COLOR_SS)
    def armUpdateSlot(self, isArmed):
        self.setText("ROV Armed" if isArmed else "ROV Disarmed")
        self.setStyleSheet(ORANGE_BUTTON_BACKGROUND_COLOR_SS if isArmed else GREEN_BUTTON_BACKGROUND_COLOR_SS)



class RovSafeModeButton(QPushButton):
    def __init__(self):
        super(RovSafeModeButton, self).__init__()
        self.setText("Safe Mode On")
        self.setEnabled(True)
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)

class ArmMovementOptionsDropdown(QComboBox):
    def __init__(self):
        super(ArmMovementOptionsDropdown, self).__init__()
        self.addItems(["Travel Home", "Workspace Home", "Storage 1", "Storage 2", "Storage 3"])
        self.setMinimumHeight(BUTTON_MAX_HEIGHT)

class MoveArmButton(QPushButton):
    def __init__(self):
        super(MoveArmButton, self).__init__()
        self.setText("Move Arm")
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)

class DisplayAltitude(QLabel):
    def __init__(self):
        super(DisplayAltitude, self).__init__()
        self.setText("Altitude: Initializing...")
    def updateAltitudeSlot(self, alt):
        self.setText("Altitude: " + alt)

class DisplayTemperature(QLabel):
    def __init__(self):
        super(DisplayTemperature, self).__init__()
        self.setText("Temperature: Initializing...")
    def updateTemperatureSlot(self, temp):
        self.setText("Temperature: " + temp)

class DisplayVoltage(QLabel):
    def __init__(self):
        super(DisplayVoltage, self).__init__()
        self.setText("Voltage: Initializing...")
    def updateVoltageSlot(self, volts):
        self.setText("Voltage: " + str(volts))

class DisplayRotations(QLabel):
    def __init__(self):
        super(DisplayRotations, self).__init__()
        self.setText("Rotations: Initializing...")
        self.rotationCounter = RotationCounter()
        self.rotations = 0
    def updateRotationsSlot(self, heading):
        newRotations = round(self.rotationCounter.calculate_rotation(heading))
        if newRotations != self.rotations:
            self.rotations = newRotations
            self.setText("Rotations: " + str(self.rotations))


class HeadingLockButton(QPushButton):
    def __init__(self):
        super(HeadingLockButton, self).__init__()
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)
        self.setText("Heading Lock Off")
        self.setStyleSheet(GREY_BUTTON_BACKGROUND_COLOR_SS)
    def headingLockValueUpdateSlot(self, desiredHeading):
        if (desiredHeading == -1):
            self.setText("Heading Lock Off")
            self.setStyleSheet(GREY_BUTTON_BACKGROUND_COLOR_SS)
        else:
            self.setText("Heading Lock Set To " + str(desiredHeading))
            self.setStyleSheet(BLUE_BUTTON_BACKGROUND_COLOR_SS)
class HeadingLockTextBox(QLineEdit):
    headValueFromTextBox = pyqtSignal(str)
    def __init__(self):
        super(HeadingLockTextBox, self).__init__()
        self.setMaximumWidth(SMALL_TEXT_BOX_MAX_WIDTH)
    def sendValueSlot(self):
        self.headValueFromTextBox.emit(self.text())

class DepthLockButton(QPushButton):
    def __init__(self):
        super(DepthLockButton, self).__init__()
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)
        self.setText("Depth Lock Off")
        self.setStyleSheet(GREY_BUTTON_BACKGROUND_COLOR_SS)
    def depthLockValueUpdateSlot(self, desiredDepth):
        if (desiredDepth == -1):
            self.setText("Depth Lock Off")
            self.setStyleSheet(GREY_BUTTON_BACKGROUND_COLOR_SS)
        else:
            self.setText("Depth Lock Set To " + str(desiredDepth))
            self.setStyleSheet(BLUE_BUTTON_BACKGROUND_COLOR_SS)

class DepthLockTextBox(QLineEdit):
    depthValueFromTextBox = pyqtSignal(str)
    def __init__(self):
        super(DepthLockTextBox, self).__init__()
        self.setMaximumWidth(SMALL_TEXT_BOX_MAX_WIDTH)
    def sendValueSlot(self):
        self.depthValueFromTextBox.emit(self.text())

class LeakIndicator(QTextEdit):
    def __init__(self):
        super(LeakIndicator, self).__init__()
        self.setFixedHeight(INDICATOR_FIXED_HEIGHT)
        self.setMinimumWidth(INDICATOR_MIN_WIDTH)
        self.setReadOnly(True)
        self.setIndicatorToNotLeak()
        self.leakWasWarned = False
        self.leakWarningPopup = LeakWarningPopup()
    def setIndicatorToLeak(self):
        self.setStyleSheet(RED_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Leak Detected!")
    def setIndicatorToNotLeak(self):
        self.setStyleSheet(GREEN_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("No Leak Detected")
    def leakUpdateSlot(self, leak):
        if (leak):
            self.setIndicatorToLeak()
            if (not self.leakWasWarned):
                self.leakWasWarned = True
                self.leakWarningPopup.popup()
        else:
            self.setIndicatorToNotLeak()

class LeakWarningPopup(QMessageBox):
    def popup(self):
        self.warning(self, "Leak Detected!", "The ROV has detected a leak within the internal electronics! Return to the surface immediately!", QMessageBox.Ok)

class VoltageIndicator(QTextEdit):
    def __init__(self):
        super(VoltageIndicator, self).__init__()
        self.BATTERY_LOW_PER_CELL = 3.5
        self.BATTERY_CRITICAL_PER_CELL = 3.3
        self.NUMBER_OF_CELLS = 4
        self.setFixedHeight(INDICATOR_FIXED_HEIGHT)
        self.setMinimumWidth(INDICATOR_MIN_WIDTH)
        self.setReadOnly(True)
        self.setIndicatorToBatteryGood()
        self.batteryCriticalWasWarned = False
        self.batteryCriticalWarningPopup = BatteryCriticalWarningPopup()
    def setIndicatorToBatteryCritical(self):
        self.setStyleSheet(RED_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Battery Critical!")
    def setIndicatorToBatteryLow(self):
        self.setStyleSheet(ORANGE_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Battery Low!")
    def setIndicatorToBatteryGood(self):
        self.setStyleSheet(GREEN_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Battery Good")
    def voltageUpdateSlot(self, volts):
        if (volts>self.BATTERY_LOW_PER_CELL*self.NUMBER_OF_CELLS):
            self.setIndicatorToBatteryGood()
        elif (volts>self.BATTERY_CRITICAL_PER_CELL*self.NUMBER_OF_CELLS):
            self.setIndicatorToBatteryLow()
        elif (not self.batteryCriticalWasWarned):
            self.setIndicatorToBatteryCritical()
            self.batteryCriticalWasWarned = True
            self.batteryCriticalWarningPopup.popup()
        else:
            self.setIndicatorToBatteryCritical()

class BatteryCriticalWarningPopup(QMessageBox):
    def popup(self):
        self.warning(self, "Battery Critical!", "The ROV battery is critically low! Return to the surface immediately!", QMessageBox.Ok)

class DepthIndicator(QTextEdit):
    def __init__(self):
        super(DepthIndicator, self).__init__()
        self.DEPTH_WARNING_THRESHHOLD = 80.0
        self.DEPTH_MAX_THRESHHOLD = 90.0
        self.setFixedHeight(INDICATOR_FIXED_HEIGHT)
        self.setMinimumWidth(INDICATOR_MIN_WIDTH)
        self.setReadOnly(True)
        self.setDepthIndicatorGood()
    def setDepthIndicatorGood(self):
        self.setStyleSheet(GREEN_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Depth Good")
    def setDepthIndicatorWarning(self):
        self.setStyleSheet(ORANGE_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Approaching Max Depth!")
    def setDepthIndicatorCritical(self):
        self.setStyleSheet(RED_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Exceeded Max Depth!")
    def depthUpdateSlot(self, depth):
        if (depth<self.DEPTH_WARNING_THRESHHOLD):
            self.setDepthIndicatorGood()
        elif (depth<self.DEPTH_MAX_THRESHHOLD):
            self.setDepthIndicatorWarning()
        else:
            self.setDepthIndicatorCritical()

class PilotLogTextEntryBox(QTextEdit):
    emptyTextWroteUpon = pyqtSignal()
    def __init__(self):
        super(PilotLogTextEntryBox, self).__init__()
        self.setMinimumHeight(PILOT_LOG_MIN_HEIGHT)
        self.setMinimumWidth(PILOT_LOG_MIN_WIDTH)
        self.pilotLogFileName = '/home/rsl/Desktop/NautilusPilotLogs/Pilot Log ' + str(timeDeploymentStarted) #this should be changed so that the datetime on the video saved is the exact same as the datetime on the captains logfile to easily match them with one another
        self.entryNumber = 1
        self.pilotLogFds = open(self.pilotLogFileName, 'a')
        self.pilotLogFds.close()
    def saveTextSlot(self, comms):
        logText = self.toPlainText()
        if (len(logText) != 0):
            self.pilotLogFds = open(self.pilotLogFileName, 'a')
            self.pilotLogFds.write("Pilot's Log Entry " + str(self.entryNumber) + "\n" + str(datetime.datetime.now()) + "\n" + "Heading: " + str(comms.getHeading()) + ", Depth: " + str(comms.getDepth()) + ", Altitude: " + str(comms.getAltitude()) + ", Temperature: " + str(comms.getTemperature()) + ", Voltage: " + str(comms.getVoltage()) + ", Leak: " + ("True" if (comms.getLeak()) else "False") + ", Rotations: " + str(comms.getRotation()) + "\n")
            self.pilotLogFds.write(logText + "\n\n")
            self.entryNumber += 1
            self.pilotLogFds.close()
            self.setPlaceholderText("Saved!")
            self.clear()
    def textChangedSlot(self):
        if (len(self.toPlainText()) == 1):
            self.setPlaceholderText("")

class PilotLogSaveButton(QPushButton):
    def __init__(self):
        super(PilotLogSaveButton, self).__init__()
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)
        self.setText("Save Pilot's Log")