import sys
from pyQtWidgets import *
from PyQt5 import QtGui
from imports import * #eventually the imports file should be cleaned up...
from Comms import Comms
from VideoRetrieve import VideoRetrieve

PLACEHOLDER_IMAGE_FILE_NAME = "CameraLogo.jpg"
PLACEHOLDER_IMAGE_SIZE = (1348, 1011) #this should matchup with the size set in the run function of VideoRetrieve.py

class MainWindow(QWidget):
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

        # Depth Guage and Depth Lock (is just another compass for now...)
        #layout
        self.depthVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.depthVerticalContainer, 1, 1, 1, 2, Qt.AlignCenter)
        self.depthLockHorizontalContainer = HorizontalContainer()
        self.depthVerticalContainer.insertLayout(1, self.depthLockHorizontalContainer, Qt.AlignCenter)
        #widgets
        self.guage = gaugeWidget()
        self.depthVerticalContainer.insertWidget(0, self.guage, Qt.AlignCenter)
        self.depthLockButton = DepthLockButton()
        self.depthLockHorizontalContainer.addWidget(self.depthLockButton, Qt.AlignCenter)
        self.depthLockTextBox = DepthLockTextBox()
        self.depthLockHorizontalContainer.addWidget(self.depthLockTextBox, Qt.AlignCenter)

        # Warning Indicators
        #layout
        self.warningIndicatorsVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.warningIndicatorsVerticalContainer, 2, 1, 1, 1, Qt.AlignCenter)
        #widgets
        self.leakIndicator = LeakIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.leakIndicator, Qt.AlignCenter)
        self.voltageIndicator = VoltageIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.voltageIndicator, Qt.AlignCenter)
        self.depthIndicator = DepthIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.depthIndicator, Qt.AlignCenter)
        
        # Display Raw Values
        #layout
        self.dataValuesVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.dataValuesVerticalContainer, 2, 2, 1, 1, Qt.AlignCenter)
        #widgets
        self.displayAltitude = DisplayAltitude()
        self.dataValuesVerticalContainer.insertWidget(0, self.displayAltitude, Qt.AlignCenter)
        self.displayTemperature = DisplayTemperature()
        self.dataValuesVerticalContainer.insertWidget(1, self.displayTemperature, Qt.AlignCenter)
        self.displayVoltage = DisplayVoltage()
        self.dataValuesVerticalContainer.insertWidget(2, self.displayVoltage, Qt.AlignCenter)
        self.displayRotations = DisplayRotations()
        self.dataValuesVerticalContainer.insertWidget(3, self.displayRotations, Qt.AlignCenter)

        # Pilot's Log, Deployment Clock, and Dev Features Button
        #layouts
        self.pilotLogGridContainer = QGridLayout() #putting the captain's log in a vertical container makes it fill the width of the available space
        self.GL.addLayout(self.pilotLogGridContainer, 3, 1, 1, 2, Qt.AlignCenter)
        self.displayTimeElapsedHorizontalContainer = HorizontalContainer()
        self.pilotLogGridContainer.addLayout(self.displayTimeElapsedHorizontalContainer, 1, 1, 1, 1, Qt.AlignRight)
        #widgets
        self.pilotLogTextEntryBox = PilotLogTextEntryBox()
        self.pilotLogGridContainer.addWidget(self.pilotLogTextEntryBox, 0, 0, 1, -1, Qt.AlignLeft) # -1 means span every column
        self.pilotLogSaveButton = PilotLogSaveButton()
        self.pilotLogGridContainer.addWidget(self.pilotLogSaveButton, 1, 0, 1, 1, Qt.AlignLeft)
        self.deploymentTimer = DeploymentTimer(timeVideoStarted)
        self.displayTimeElapsedHorizontalContainer.addWidget(self.deploymentTimer.time, Qt.AlignRight)
        self.devFeaturesButton = DevFeaturesButton()
        self.displayTimeElapsedHorizontalContainer.addWidget(self.devFeaturesButton, Qt.AlignRight)

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
        self.comms.altitudeUpdate.connect(self.displayAltitude.updateAltitudeSlot)
        self.comms.temperatureUpdate.connect(self.displayTemperature.updateTemperatureSlot)
        self.comms.voltageUpdate.connect(self.displayVoltage.updateVoltageSlot)
        self.comms.headUpdate.connect(self.compass.setAngle) #slot/signal to connect compass to update function
        self.comms.headUpdate.connect(self.displayRotations.updateRotationsSlot) #calculate rotations based on heading update
        #indicators
        self.comms.leakUpdate.connect(self.leakIndicator.leakUpdateSlot)
        self.comms.voltageUpdate.connect(self.voltageIndicator.voltageUpdateSlot)
        self.comms.depthUpdate.connect(self.depthIndicator.depthUpdateSlot)
        #pilot's log
        self.pilotLogSaveButton.clicked.connect(lambda: self.pilotLogTextEntryBox.saveTextSlot(self.comms, self.deploymentTimer))
        self.pilotLogTextEntryBox.textChanged.connect(self.pilotLogTextEntryBox.textChangedSlot)
        #arm ROV
        self.rovArmedButton.clicked.connect(self.comms.armRovSlot)
        self.comms.armUpdate.connect(self.rovArmedButton.armUpdateSlot)
        #heading lock
        self.headingLockButton.clicked.connect(self.headingLockTextBox.sendValueSlot) #when heading lock button clicked, call on text box to emit a signal with the current value
        self.headingLockTextBox.headValueFromTextBox.connect(self.comms.setHeadingLockSlot) #when the text box emits its current value, comms class gets that value and sets heading lock based on it (setHeadingLockSlot)
        self.comms.headingLockValueUpdate.connect(self.headingLockButton.headingLockValueUpdateSlot) #when the heading lock value is updated (signal sent at the end of setHeadingLockSlot) update the button to reflect the current lock value
        #depth lock
        self.depthLockButton.clicked.connect(self.depthLockTextBox.sendValueSlot) #when depth lock button clicked, call on text box to emit a signal with the current value
        self.depthLockTextBox.depthValueFromTextBox.connect(self.comms.setDepthLockSlot) #when the text box emits its current value, comms class gets that value and sets depth lock based on it (setDepthLockSlot)
        self.comms.depthLockValueUpdate.connect(self.depthLockButton.depthLockValueUpdateSlot) #when the depth lock value is updated (signal sent at the end of setDepthLockSlot) update the button to reflect the current lock value
        #General
        self.setWindowTitle('Nautilus')
        self.setLayout(self.GL)

    def ImageUpdateSlot(self, Image):
        self.feedLabel.setPixmap(QPixmap.fromImage(Image)) #display a frame on the feedLabel object in the GUI

    def StopVideo(self): #calls Video Retrieval thread to stop capturing video
        self.videoRetrieve.stop()
    def StopComms(self): #calls Comms thread to stop sending and receiving messages with arduino
        self.comms.stop()

    def closeEvent(self, event):
        confirm = QMessageBox.question(self, "Quit?", "Are you sure you want to quit the application?", QMessageBox.Yes, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            #stop each thread
            self.StopComms()
            print("Comms stopped!")
            self.StopVideo()
            print("Video stopped!")
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = MainWindow()
    gui.showMaximized()
    sys.exit(App.exec())