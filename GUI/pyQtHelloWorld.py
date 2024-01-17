import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.GL = QGridLayout()
        self.FeedLabel = QLabel()
        self.GL.addWidget(self.FeedLabel)
        self.setLayout(self.GL)
        self.VideoRetrieve = VideoRetrieve() #start instance of Qthread class
        self.VideoRetrieve.start()
        self.VideoRetrieve.ImageUpdate.connect(self.ImageUpdateSlot)
        self.setWindowTitle('Video Feed')

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def StopVideo(self):
        self.VideoRetrieve.stop()

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
    def stopVideo(self):
        self.ThreadActive = False
        self.quit()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(App.exec())



