import sys
from pyQtWidgets import *
from imports import * #eventually the imports file should be cleaned up...
from Comms import Comms
from VideoRetrieve import VideoRetrieve

class MainWindow(QWidget):
    def __init__(self):
        #GUI:
        super(MainWindow, self).__init__()
        self.GL = QGridLayout()

        self.dataValuesVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.dataValuesVerticalContainer, 2, 2, 1, 1, Qt.AlignCenter)

        self.pilotLogVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.pilotLogVerticalContainer, 3, 1, 1, 2)

        self.headingLockHorizontalContainer = HorizontalContainer()
        self.GL.addLayout(self.headingLockHorizontalContainer, 4, 1, 1, 1, Qt.AlignTop)

        self.depthLockHorizontalContainer = HorizontalContainer()
        self.GL.addLayout(self.depthLockHorizontalContainer, 4, 2, 1, 1, Qt.AlignCenter)

        self.movementControlButtonsVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.movementControlButtonsVerticalContainer, 5, 1, 1, 1, Qt.AlignCenter)

        self.armLocationSelectVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.armLocationSelectVerticalContainer, 5, 2, 1, 1, Qt.AlignCenter)

        #Widgets:
        # Camera Feed
        self.feedLabel = QLabel() #object on which the pixelmap will appear in the GUI
        self.GL.addWidget(self.feedLabel, 0, 0, -1, 1, Qt.AlignCenter) #add object for camera feed pixelmap to appear on
        
        # Compass / Heading Display
        self.compass = CompassWidget()
        self.GL.addWidget(self.compass, 0, 1, 1, 2, Qt.AlignCenter)
        # Heading Lock
        self.headingLockButton = HeadingLockButton()
        self.headingLockHorizontalContainer.addWidget(self.headingLockButton, Qt.AlignCenter)
        self.headingLockTextBox = HeadingLockTextBox()
        self.headingLockHorizontalContainer.addWidget(self.headingLockTextBox, Qt.AlignCenter)

        #depth lock
        self.depthLockButton = DepthLockButton()
        self.depthLockHorizontalContainer.addWidget(self.depthLockButton, Qt.AlignCenter)
        self.depthLockTextBox = DepthLockTextBox()
        self.depthLockHorizontalContainer.addWidget(self.depthLockTextBox, Qt.AlignCenter)
        #guage (is just another compass for now...)
        self.guage = CompassWidget()
        self.GL.addWidget(self.guage, 1, 1, 1, 2, Qt.AlignCenter)

        # Warning Indicators
        self.warningIndicatorsVerticalContainer = VerticalContainer()
        self.GL.addLayout(self.warningIndicatorsVerticalContainer, 2, 1, 1, 1, Qt.AlignCenter)
        self.leakIndicator = LeakIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.leakIndicator, Qt.AlignCenter)
        self.voltageIndicator = VoltageIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.voltageIndicator, Qt.AlignCenter)
        self.depthIndicator = DepthIndicator()
        self.warningIndicatorsVerticalContainer.addWidget(self.depthIndicator, Qt.AlignCenter)

        #movement control buttons
        self.rovArmedButton = RovArmedButton()
        self.movementControlButtonsVerticalContainer.addWidget(self.rovArmedButton, Qt.AlignCenter)
        self.rovSafeModeButton = RovSafeModeButton()
        self.movementControlButtonsVerticalContainer.addWidget(self.rovSafeModeButton, Qt.AlignCenter)
        
        #arm movement
        self.armMovementOptionsDropdown = ArmMovementOptionsDropdown()
        self.armLocationSelectVerticalContainer.addWidget(self.armMovementOptionsDropdown, Qt.AlignCenter)
        self.moveArmButton = MoveArmButton()
        self.armLocationSelectVerticalContainer.addWidget(self.moveArmButton, Qt.AlignCenter)
        
        #display raw values
        self.displayAltitude = DisplayAltitude()
        self.dataValuesVerticalContainer.insertWidget(0, self.displayAltitude, Qt.AlignCenter)
        self.displayTemperature = DisplayTemperature()
        self.dataValuesVerticalContainer.insertWidget(1, self.displayTemperature, Qt.AlignCenter)
        self.displayVoltage = DisplayVoltage()
        self.dataValuesVerticalContainer.insertWidget(2, self.displayVoltage, Qt.AlignCenter)
        self.displayRotations = DisplayRotations()
        self.dataValuesVerticalContainer.insertWidget(3, self.displayRotations, Qt.AlignCenter)
        
        # Pilot's Log
        self.pilotLogTextEntryBox = PilotLogTextEntryBox()
        self.pilotLogVerticalContainer.addWidget(self.pilotLogTextEntryBox, Qt.AlignCenter)
        self.pilotLogSaveButton = PilotLogSaveButton()
        self.pilotLogVerticalContainer.addWidget(self.pilotLogSaveButton, Qt.AlignCenter)

        #Threading:
        self.videoRetrieve = VideoRetrieve() #create instance of Qthread class
        self.comms = Comms() #create instance of Qthread class
        self.videoRetrieve.start() #start instance of Qthread class
        self.comms.start() #start instance of Qthread class
        
        #Slots and Signals
        self.videoRetrieve.ImageUpdate.connect(self.ImageUpdateSlot)
        self.comms.altitudeUpdate.connect(self.displayAltitude.updateAltitudeSlot)
        self.comms.temperatureUpdate.connect(self.displayTemperature.updateTemperatureSlot)
        self.comms.voltageUpdate.connect(self.displayVoltage.updateVoltageSlot)
        self.comms.headUpdate.connect(self.compass.setAngle) #slot/signal to connect compass to update function
        self.comms.leakUpdate.connect(self.leakIndicator.leakUpdateSlot)
        self.comms.voltageUpdate.connect(self.voltageIndicator.voltageUpdateSlot)
        self.comms.depthUpdate.connect(self.depthIndicator.depthUpdateSlot)
        self.pilotLogSaveButton.clicked.connect(lambda: self.pilotLogTextEntryBox.saveTextSlot(self.comms))
        self.rovArmedButton.clicked.connect(self.comms.armRovSlot)
        self.comms.armUpdate.connect(self.rovArmedButton.armUpdateSlot)
        self.headingLockButton.clicked.connect(self.headingLockTextBox.sendValueSlot) #when heading lock button clicked, call on text box to emit a signal with the current value
        self.headingLockTextBox.headValueFromTextBox.connect(self.comms.setHeadingLockSlot) #when the text box emits its current value, comms class gets that value and sets heading lock based on it (setHeadingLockSlot)
        self.comms.headingLockValueUpdate.connect(self.headingLockButton.headingLockValueUpdateSlot) #when the heading lock value is updated (signal sent at the end of setHeadingLockSlot) update the button to reflect the current lock value
        self.pilotLogTextEntryBox.textChanged.connect(self.pilotLogTextEntryBox.textChangedSlot)
        
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
    gui.show()
    sys.exit(App.exec())