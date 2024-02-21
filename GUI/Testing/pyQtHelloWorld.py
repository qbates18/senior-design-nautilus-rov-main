### TESTING

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.GL = QGridLayout()
        self.FeedLabel = QLabel() #object on which the pixelmap will appear in the GUI
        self.GL.addWidget(self.FeedLabel, 0, 0, Qt.AlignCenter)
        self.VideoRetrieve = VideoRetrieve() #create instance of Qthread class
        self.VideoRetrieve.start() #start instance of Qthread class
        self.VideoRetrieve.ImageUpdate.connect(self.ImageUpdateSlot)
        self.setWindowTitle('Video Feed')
        self.setLayout(self.GL)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image)) #display a frame on the FeedLabel object in the GUI

    def StopVideo(self): #calls Video Retrieval thread to stop capturing video
        self.VideoRetrieve.stop()
    
    def closeEvent(self, event):
        confirm = QMessageBox.question(self, "Quit?", "Are you sure you want to quit the application?", QMessageBox.Yes, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            self.StopVideo()
            event.accept()
        else:
            event.ignore()


class VideoRetrieve(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        cap = cv2.VideoCapture(0) #make a connection with the camera
        while self.ThreadActive:
            ret, frame = cap.read() #capture a frame
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888) #pass in binary values of the flipped image, converting frame to a QImage
                Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic) #emit the QImage
    def stop(self):
        self.ThreadActive = False
        self.quit()
        self.wait()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(App.exec())

