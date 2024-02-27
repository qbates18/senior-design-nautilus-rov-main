from PyQt5.QtGui import *
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
from imports import timeDeploymentStarted, timeVideoStarted
from imports import RotationCounter
import config

BUTTON_MAX_HEIGHT = 40
BUTTON_MAX_WIDTH = 175
BUTTON_MIN_HEIGHT = 40
SHORTER_BUTTON_MIN_HEIGHT = 30
BUTTON_MIN_WIDTH = 175

CLOCK_MAX_WIDTH = round(BUTTON_MIN_WIDTH/2)
CLOCK_MIN_WIDTH = CLOCK_MAX_WIDTH

DEV_BUTTON_MAX_HEIGHT = BUTTON_MAX_HEIGHT
DEV_BUTTON_MAX_WIDTH = 80
DEV_BUTTON_MIN_HEIGHT = 30
DEV_BUTTON_MIN_WIDTH = DEV_BUTTON_MAX_WIDTH

GREEN_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(30, 255, 30, 60%);"
ORANGE_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(255, 175, 5, 60%);"
RED_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(255, 30, 30, 60%);"
BLUE_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(75, 150, 255, 60%)"
GREY_BUTTON_BACKGROUND_COLOR_SS = "background-color : rgba(128, 128, 128, 60%)"

QCOLOR_BLUE = QColor(75, 150, 255, 100)
QCOLOR_GREY = QColor(128, 128, 126, 100)

SMALL_TEXT_BOX_MAX_WIDTH = 40

COMPASS_FIXED_WIDTH = 200
COMPASS_FIXED_HEIGHT = 200

INDICATOR_FIXED_HEIGHT = 40
INDICATOR_MIN_WIDTH = 80

PILOT_LOG_MIN_WIDTH = 460

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
        
        painter.setBrush(QBrush(QCOLOR_BLUE))
        
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

class gaugeWidget(QWidget):

    angleChanged = pyqtSignal(float)

    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)

        self._angle = 0.0
        self._margins = 10
        self.setFixedWidth(COMPASS_FIXED_WIDTH)
        self.setFixedHeight(COMPASS_FIXED_HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.drawCircleGauge(painter)
        #self.drawColor(painter)
        self.drawMarkings(painter)
        self.drawNeedle(painter)
        
        painter.end()

    def drawNeedle(self, painter):

        painter.save()
        painter.translate(self.width()/2, (self.height()/2)+10)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(QCOLOR_GREY,  2, Qt.SolidLine))
        painter.setBrush(QBrush(QCOLOR_BLUE, Qt.SolidPattern))
        painter.drawEllipse(-5, -5, 10, 10)

        painter.rotate(self._angle)

        painter.setPen(QPen(QCOLOR_BLUE, 2, Qt.SolidLine))
        painter.setBrush(QBrush(QCOLOR_BLUE, Qt.SolidPattern))
        points = [
            QPoint(0,0),
            QPoint(-36,36),
            ]
        poly = QPolygon(points)
        painter.drawPolygon(poly)

        painter.restore()

    def drawCircleGauge(self, painter):
        painter.save()

        painter.translate(self.width()/2, (self.height()/2)+10)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        painter.drawArc(-44, -44, 88, 88, -45 * 16, 270 * 16)

        painter.restore()

    def drawColor(self, painter):
        painter.save()

        painter.translate(self.width()/2, (self.height()/2)+10)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.green, 4, Qt.SolidLine))
        painter.drawArc(-44, -44, 92, 92, 10 * 16, 215 * 16)

        painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
        painter.drawArc(-44, -44, 92, 92, -45 * 16, 58 * 16)

        painter.restore()

    def drawMarkings(self, painter):
        
        painter.save()
        painter.translate((self.width()/2), (self.height()/2)+10)
        scale = min((self.width() - self._margins)/120.0,
                    (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)
        painter.setPen(QPen(Qt.gray, 2, Qt.SolidLine))

        i = 0
        
        while i < 283:
        
            if i % 45 == 0:
                painter.drawLine(-30, 30, -38, 38)
            else:
                painter.drawLine(-30, 30, -38, 38)
            
            painter.rotate(15)
            i += 15
        
        painter.restore()
    
    def angle(self):
        return self._angle

    @pyqtSlot(float)
    def setAngle(self, angle):
        angle = ((angle*270)/config.NAUTILUS_MAX_RATED_DEPTH)
        if angle > 270:
            angle = 270
    
        if angle != self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()
    

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
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)
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
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)

class ArmMovementOptionsDropdown(QComboBox):
    def __init__(self):
        super(ArmMovementOptionsDropdown, self).__init__()
        self.addItems(["Travel Home", "Workspace Home", "Storage 1", "Storage 2", "Storage 3"])
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)

class MoveArmButton(QPushButton):
    def __init__(self):
        super(MoveArmButton, self).__init__()
        self.setText("Move Arm")
        self.setMaximumWidth(BUTTON_MAX_WIDTH)
        self.setMaximumHeight(BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)

class DisplayAltitude(QLabel):
    def __init__(self):
        super(DisplayAltitude, self).__init__()
        self.setText("Altitude: Initializing...")
    def updateAltitudeSlot(self, alt):
        self.setText("Altitude: " + str(alt) + " m")

class DisplayTemperature(QLabel):
    def __init__(self):
        super(DisplayTemperature, self).__init__()
        self.setText("Temperature: Initializing...")
    def updateTemperatureSlot(self, temp):
        self.setText("Temperature: " + temp + " " + u'\N{DEGREE SIGN}' + "C")

class DisplayVoltage(QLabel):
    def __init__(self):
        super(DisplayVoltage, self).__init__()
        self.setText("Voltage: Initializing...")
    def updateVoltageSlot(self, volts):
        self.setText("Voltage: " + str(volts) + " V")

class DisplayRotations(QLabel):
    def __init__(self):
        super(DisplayRotations, self).__init__()
        self.setText("Rotations: Initializing...")
        self.rotationCounter = RotationCounter()
        self.rotations = None
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
        self.setMinimumHeight(SHORTER_BUTTON_MIN_HEIGHT)
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
        self.setMinimumHeight(SHORTER_BUTTON_MIN_HEIGHT)
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
        self.setStyleSheet(ORANGE_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Leak Sensor Initializing...")
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
        self.setStyleSheet(ORANGE_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Battery Indicator Initializing...")
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
        self.DEPTH_WARNING_THRESHHOLD = config.NAUTILUS_MAX_RATED_DEPTH - (config.NAUTILUS_MAX_RATED_DEPTH*0.2) #warn when only 20% of max rated depth remains
        self.DEPTH_MAX_THRESHHOLD = config.NAUTILUS_MAX_RATED_DEPTH - (config.NAUTILUS_MAX_RATED_DEPTH*0.1) #warn/notify when only 10% of max rated depth remains
        self.setFixedHeight(INDICATOR_FIXED_HEIGHT)
        self.setMinimumWidth(INDICATOR_MIN_WIDTH)
        self.setReadOnly(True)
        self.setStyleSheet(ORANGE_BUTTON_BACKGROUND_COLOR_SS)
        self.setText("Depth Indicator Initializing...")
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
        self.setMinimumWidth(PILOT_LOG_MIN_WIDTH)
        self.pilotLogFileName = '/home/rsl/Desktop/NautilusCaptain\'sLogs/Captain\'s Log ' + str(timeDeploymentStarted) #this should be changed so that the datetime on the video saved is the exact same as the datetime on the captains logfile to easily match them with one another
        self.entryNumber = 1
        self.pilotLogFds = None
    def saveTextSlot(self, comms, timer):
        logText = self.toPlainText()
        if (len(logText) != 0):
            self.pilotLogFds = open(self.pilotLogFileName, 'a')
            self.pilotLogFds.write("Captain's Log Entry " + str(self.entryNumber) + "\n"
                                   + str(datetime.datetime.now())[0:19]+ ", " + timer.getTime() + " since deployment start" + "\n" #0 to 19 so that the decimal gets left out.
                                   + "Heading: " + str(comms.getHeading())
                                   + ", Depth: " + str(comms.getDepth())
                                   + " m, Altitude: " + str(comms.getAltitude())
                                   + " m, Temperature: " + str(comms.getTemperature()) + " " + u'\N{DEGREE SIGN}'
                                   + "C, Voltage: " + str(comms.getVoltage())
                                   + " V, Leak: " + ("True" if (comms.getLeak()) else "False")
                                   + ", Rotations: " + str(comms.getRotation()) + "\n")
            self.pilotLogFds.write(logText + "\n\n")
            self.pilotLogFds.close()
            self.entryNumber += 1
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
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.setText("Save Captain's Log")


class DisplayTimeElapsed(QLabel):
    def __init__(self):
        super(DisplayTimeElapsed, self).__init__()
        self.setMaximumWidth(CLOCK_MAX_WIDTH)
        self.setMinimumWidth(CLOCK_MIN_WIDTH)
        self.setText("Clock: Initializing...")

class DevToolsButton(QPushButton):
    def __init__(self):
        super(DevToolsButton, self).__init__()
        self.setMaximumWidth(DEV_BUTTON_MAX_WIDTH)
        self.setMaximumHeight(DEV_BUTTON_MAX_HEIGHT)
        self.setMinimumWidth(DEV_BUTTON_MIN_WIDTH)
        self.setMinimumHeight(DEV_BUTTON_MIN_HEIGHT)
        self.setText("Dev Tools")
        self.devToolsWindow = DevToolsWindow()
    def openDevToolsSlot(self):
        print("Opening Dev Tools!")
        self.devToolsWindow.show()
        return

class DevToolsWindow(QDialog):
    devToolsUpdateSignal = pyqtSignal(dict)
    # constructor
    def __init__(self):
        super(DevToolsWindow, self).__init__()
        self.listOfItems = ["first", "second"]
        self.devToolsItemsDict = {self.listOfItems[0]: None, self.listOfItems[1]: None}
        self.setWindowTitle("Dev Tools")
        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)
        # creating a group box
        self.formGroupBox = QGroupBox("Modify Settings:")
        
        self.item0LineEdit = QLineEdit()
        self.item1LineEdit = QLineEdit()

        self.createForm()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.getInfo)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
   
    # get info method called when form is accepted
    def getInfo(self):
        # printing the form information
        self.devToolsItemsDict[self.listOfItems[0]] = self.item0LineEdit.text()
        self.devToolsItemsDict[self.listOfItems[1]] = self.item1LineEdit.text()
        # closing the window
        self.close()
        self.devToolsUpdateSignal.emit(self.devToolsItemsDict)
        return
    
    # create form method
    def createForm(self):
        # creating a form layout
        layout = QFormLayout()
        # adding rows
        layout.addRow(QLabel(self.listOfItems[0]), self.item0LineEdit)
        layout.addRow(QLabel(self.listOfItems[1]), self.item1LineEdit)
        
        #set the layout
        self.formGroupBox.setLayout(layout)


# Requires the start time!
class DeploymentTimer(QWidget):
    def __init__(self, start):
        super().__init__()
        self._start = start

        # Timer/Stopwatch Display
        self.time = QLabel()
        self.time.setMaximumWidth(CLOCK_MAX_WIDTH)
        self.time.setMinimumWidth(CLOCK_MIN_WIDTH)
        self.time.setText("00:00:00")

        # Background Timer -- updates the onscreen display every 1000 milliseconds (not shown)
        timer = QTimer(self)
        timer.timeout.connect(self.updateTime) # see updateTime for specific behavior
        timer.start(1000) # this will cause the time to update every 1000 milliseconds

    # Returns a human-friendly time since deployment started as a string in the form HH:MM:SS
    def getTime(self):
        if (self._start is None):
            return "00:00:00"
        timeDiff = datetime.datetime.now() - self._start
        total = timeDiff.total_seconds()
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    
    # Updates the text in self.time (the timer/stopwatch) to the current time since deployment started
    def updateTime(self):
        self.time.setText(self.getTime())
    
    def videoStartedSlot(self, timeStarted):
        self._start = timeStarted