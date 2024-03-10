import sys
from pyQtWidgets import *
from PyQt5 import QtGui
from imports import * #eventually the imports file should be cleaned up...
from Comms import Comms
from VideoRetrieve import VideoRetrieve

PLACEHOLDER_IMAGE_FILE_NAME = "CameraLogo.jpg"
SHUTDOWN_IMAGE_FILE_NAME = "ShuttingDown.jpg"
PLACEHOLDER_IMAGE_SIZE = config.VideoSize

class MainWindow(QWidget):
    stopCommsSignal = pyqtSignal()
    def __init__(self):
        #GUI:
        super(MainWindow, self).__init__()
        self.GL = QGridLayout()

        # Camera Feed
        self.feedLabel = QLabel() #object on which the pixelmap will appear in the GUI
        self.GL.addWidget(self.feedLabel, 0, 0, -1, 1, Qt.AlignCenter) #add object for camera feed pixelmap to appear on
        #show placeholder image
        self.feedLabel.setPixmap(QtGui.QPixmap(PLACEHOLDER_IMAGE_FILE_NAME).scaled(PLACEHOLDER_IMAGE_SIZE[0], PLACEHOLDER_IMAGE_SIZE[1]))
        
        # Compass / Heading Display and Heading Lock
        #layout
        self.headingVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.headingVerticalContainer, 0, 1, 1, 2, Qt.AlignCenter)
        self.headingLockHorizontalContainer = HorizontalContainer()
        self.headingVerticalContainer.insertLayout(1, self.headingLockHorizontalContainer, Qt.AlignCenter)
        #widgets
        self.compass = CompassWidget()
        self.headingVerticalContainer.insertWidget(0, self.compass, Qt.AlignRight)
        self.headingLockButton = HeadingLockButton()
        self.headingLockHorizontalContainer.addWidget(self.headingLockButton, Qt.AlignCenter)
        self.headingLockTextBox = HeadingLockTextBox()
        self.headingLockHorizontalContainer.addWidget(self.headingLockTextBox, Qt.AlignCenter)

        # Depth Guage, Depth Lock, Altitude Lock
        #layout
        self.depthVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.depthVerticalContainer, 1, 1, 1, 2, Qt.AlignCenter)
        self.depthLockHorizontalContainer = HorizontalContainer()
        self.depthVerticalContainer.insertLayout(1, self.depthLockHorizontalContainer, Qt.AlignCenter)
        #widgets
        self.gauge = gaugeWidget()
        self.depthVerticalContainer.insertWidget(0, self.gauge, Qt.AlignCenter)
        self.depthLockButton = DepthLockButton()
        self.depthLockHorizontalContainer.addWidget(self.depthLockButton, Qt.AlignCenter)
        self.depthLockTextBox = DepthLockTextBox()
        self.depthLockHorizontalContainer.addWidget(self.depthLockTextBox, Qt.AlignCenter)

        #Altitude Lock
        self.altitudeVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.altitudeVerticalContainer, 2, 1, 1, 2, Qt.AlignCenter)
        self.altitudeLockHorizontalContainer = HorizontalContainer()
        self.altitudeVerticalContainer.insertLayout(0, self.altitudeLockHorizontalContainer, Qt.AlignCenter)

        self.altitudeLockButton = altitudeLockButton()
        self.altitudeLockHorizontalContainer.addWidget(self.altitudeLockButton, Qt. AlignCenter)
        self.altitudeLockTextBox = altitudeLockTextBox()
        self.altitudeLockHorizontalContainer.addWidget(self.altitudeLockTextBox, Qt. AlignCenter)

        # Warning Indicators
        #layout
        self.warningIndicatorsVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.warningIndicatorsVerticalContainer, 3, 1, 1, 1, Qt.AlignCenter)
        #widgets
        self.depthIndicator = DepthIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.depthIndicator, Qt.AlignCenter)
        
        self.leakIndicator = LeakIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.leakIndicator, Qt.AlignCenter)

        self.voltageIndicator = VoltageIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.voltageIndicator, Qt.AlignCenter)

        self.commsIndicator = CommsIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.commsIndicator, Qt.AlignCenter)
        
        # Display Raw Values
        #layout
        self.dataValuesVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.dataValuesVerticalContainer, 3, 2, 1, 1, Qt.AlignCenter)
        #widgets
        self.displayDepth = DisplayDepth()
        self.dataValuesVerticalContainer.insertWidget(0, self.displayDepth, Qt.AlignCenter)
        self.displayAltitude = DisplayAltitude()
        self.dataValuesVerticalContainer.insertWidget(1, self.displayAltitude, Qt.AlignCenter)
        self.displayTemperature = DisplayTemperature()
        self.dataValuesVerticalContainer.insertWidget(2, self.displayTemperature, Qt.AlignCenter)
        self.displayVoltage = DisplayVoltage()
        self.dataValuesVerticalContainer.insertWidget(3, self.displayVoltage, Qt.AlignCenter)
        self.displayRotations = DisplayRotations()
        self.dataValuesVerticalContainer.insertWidget(4, self.displayRotations, Qt.AlignCenter)

        # Captain's Log, Deployment Clock, and Dev Tools Button
        #layouts
        self.captainLogGridContainer = QGridLayout() #putting the captain's log in a vertical container makes it fill the width of the available space
        self.GL.addLayout(self.captainLogGridContainer, 4, 1, 1, 2, Qt.AlignCenter)
        self.displayTimeElapsedHorizontalContainer = HorizontalContainer()
        self.captainLogGridContainer.addLayout(self.displayTimeElapsedHorizontalContainer, 1, 1, 1, 1, Qt.AlignRight)
        #widgets
        self.captainLogTextEntryBox = CaptainLogTextEntryBox()
        self.captainLogGridContainer.addWidget(self.captainLogTextEntryBox, 0, 0, 1, -1, Qt.AlignLeft) # -1 means span every column
        self.captainLogSaveButton = CaptainLogSaveButton()
        self.captainLogGridContainer.addWidget(self.captainLogSaveButton, 1, 0, 1, 1, Qt.AlignLeft)
        self.deploymentTimer = DeploymentTimer(timeVideoStarted)
        self.displayTimeElapsedHorizontalContainer.addWidget(self.deploymentTimer.time, Qt.AlignRight)
        self.devToolsButton = DevToolsButton()
        self.displayTimeElapsedHorizontalContainer.addWidget(self.devToolsButton, Qt.AlignRight)
        self.devToolsWindow = DevToolsWindow()
        
        # Movement Control Buttons
        #layout
        self.movementControlButtonsVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.movementControlButtonsVerticalContainer, 5, 1, 1, 1, Qt.AlignLeft)
        #widgets
        self.rovArmedButton = RovArmedButton()
        self.movementControlButtonsVerticalContainer.addWidget(self.rovArmedButton, Qt.AlignLeft)
        self.rovSafeModeButton = RovSafeModeButton()
        self.movementControlButtonsVerticalContainer.addWidget(self.rovSafeModeButton, Qt.AlignLeft)

        # Arm Movement
        #layout
        self.armLocationSelectVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.armLocationSelectVerticalContainer, 5, 2, 1, 1, Qt.AlignRight)
        #widgets
        self.armMovementOptionsDropdown = ArmMovementOptionsDropdown()
        self.armLocationSelectVerticalContainer.addWidget(self.armMovementOptionsDropdown, Qt.AlignCenter)
        self.moveArmButton = MoveArmButton()
        self.armLocationSelectVerticalContainer.addWidget(self.moveArmButton, Qt.AlignCenter)

        #Threading
        self.videoRetrieve = VideoRetrieve() #create instance of Qthread class
        self.comms = Comms() #create instance of Qthread class
        self.videoRetrieve.start() #start instance of Qthread class
        self.comms.start() #start instance of Qthread class
        
        # Slots and Signals
        #video update
        self.videoRetrieve.ImageUpdate.connect(self.ImageUpdateSlot)
        #video timer start
        self.videoRetrieve.videoStartSignal.connect(self.deploymentTimer.videoStartedSlot)
        #sensor data updates
        self.comms.headUpdate.connect(self.compass.setAngle) #slot/signal to connect compass to update function
        self.comms.depthUpdate.connect(self.gauge.setAngle) #slot/signal to connect gauge to update function

        self.comms.depthUpdate.connect(self.displayDepth.updateDepthSlot)
        self.comms.altitudeUpdate.connect(self.displayAltitude.updateAltitudeSlot)
        self.comms.temperatureUpdate.connect(self.displayTemperature.updateTemperatureSlot)
        self.comms.voltageUpdate.connect(self.displayVoltage.updateVoltageSlot)
        self.comms.headUpdate.connect(self.displayRotations.updateRotationsSlot) #calculate rotations based on heading update
        #indicators
        self.comms.leakUpdate.connect(self.leakIndicator.leakUpdateSlot)
        self.comms.commsStatusUpdate.connect(self.leakIndicator.commsStatusSlot)

        self.comms.voltageUpdate.connect(self.voltageIndicator.voltageUpdateSlot)
        self.comms.commsStatusUpdate.connect(self.voltageIndicator.commsStatusSlot)

        self.comms.depthUpdate.connect(self.depthIndicator.depthUpdateSlot)
        self.comms.commsStatusUpdate.connect(self.depthIndicator.commsStatusSlot)

        self.comms.commsStatusUpdate.connect(self.commsIndicator.commsIndicatorUpdateSlot)
        #captain's log
        self.captainLogSaveButton.clicked.connect(lambda: self.captainLogTextEntryBox.saveTextSlot(self.deploymentTimer))
        self.captainLogTextEntryBox.textChanged.connect(self.captainLogTextEntryBox.textChangedSlot)
        #arm ROV
        self.rovArmedButton.clicked.connect(self.comms.armRovSlot)
        self.comms.armUpdate.connect(self.rovArmedButton.armUpdateSlot)
        #safe mode
        self.rovSafeModeButton.clicked.connect(self.comms.safemodeSlot)
        self.comms.safemodeUpdate.connect(self.rovSafeModeButton.safemodeUpdateSlot)

        #heading lock
        self.headingLockButton.clicked.connect(self.headingLockTextBox.sendValueSlot) #when heading lock button clicked, call on text box to emit a signal with the current value
        self.headingLockTextBox.headValueFromTextBox.connect(self.comms.setHeadingLockSlot) #when the text box emits its current value, comms class gets that value and sets heading lock based on it (setHeadingLockSlot)
        self.comms.headingLockValueUpdate.connect(self.headingLockButton.headingLockValueUpdateSlot) #when the heading lock value is updated (signal sent at the end of setHeadingLockSlot) update the button to reflect the current lock value
        #depth lock
        self.depthLockButton.clicked.connect(self.depthLockTextBox.sendValueSlot) #when depth lock button clicked, call on text box to emit a signal with the current value
        self.depthLockTextBox.depthValueFromTextBox.connect(self.comms.setDepthLockSlot) #when the text box emits its current value, comms class gets that value and sets depth lock based on it (setDepthLockSlot)
        self.comms.depthLockValueUpdate.connect(self.depthLockButton.depthLockValueUpdateSlot) #when the depth lock value is updated (signal sent at the end of setDepthLockSlot) update the button to reflect the current lock value
        #dev tools
        self.devToolsButton.clicked.connect(self.devToolsWindow.openDevToolsSlot)
        self.devToolsWindow.devToolsUpdateSignal.connect(self.comms.devToolsItemsDictUpdateSlot) #when the devtools window is saved update the comms classes pid gains dictionary
        self.comms.addArduinoErrorMessageUpdate.connect(self.devToolsWindow.arduinoErrorsTextEdit.addErrorSlot) #add messages with ampersands to the devtools window, these messages are supposed to be errors received from the arduino
        #ending the program, one thread at a time...
        self.threadsFinished = False
        self.stopCommsSignal.connect(self.comms.stopSlot)
        self.comms.finished.connect(self.videoRetrieve.stopSlot)
        self.videoRetrieve.finished.connect(self.stopProgramSlot)

        #General
        self.setWindowTitle('Nautilus')
        self.setLayout(self.GL)

    # Updating Developer Tools Values:
    def updateDevToolsValues(self, devToolsItemsDict):
        print(devToolsItemsDict)

    # Updating the Camera frame
    def ImageUpdateSlot(self, Image):
        self.feedLabel.setPixmap(QPixmap.fromImage(Image)) #display a frame on the feedLabel object in the GUI

    # Stopping the program:
    def closeEvent(self, event):
        if self.threadsFinished:
            event.accept()
            return
        else:
            confirm = QMessageBox.question(self, "Quit?", "Are you sure you want to quit the application?", QMessageBox.Yes, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                # use slots and signals to stop each thread
                print("Request Program Shutdown")
                self.stopCommsSignal.emit()
                event.ignore()
                return
            if confirm == QMessageBox.No:
                event.ignore()
    
    def stopProgramSlot(self):
        #wait for threads to finish
        self.comms.wait()
        self.videoRetrieve.wait()
        #threads are finished, set shutdown image and wait one second (for any remaining I/O)
        self.feedLabel.setPixmap(QtGui.QPixmap(SHUTDOWN_IMAGE_FILE_NAME).scaled(PLACEHOLDER_IMAGE_SIZE[0], PLACEHOLDER_IMAGE_SIZE[1]))
        print("Program Shutdown Successful")
        QTimer.singleShot(1000, self.threadsAreFinishedSlot) #wait 1 seconds before fully closing program
    
    @pyqtSlot()
    def threadsAreFinishedSlot(self):
        self.threadsFinished = True
        self.devToolsWindow.close() #close the devtools window if it's open
        self.close() #now that threads are finished, closeEvent slot will execute the True case and event.accept()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = MainWindow()
    gui.showMaximized()
    sys.exit(App.exec())