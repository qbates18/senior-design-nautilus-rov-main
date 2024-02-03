import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
import gi
import numpy as np
import datetime

gi.require_version('Gst', '1.0')
from gi.repository import Gst

class CompassWidget(QWidget):

    angleChanged = pyqtSignal(float)
    
    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        self._angle = 0.0
        self._margins = 10
        self._pointText = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S",
                           225: "SW", 270: "W", 315: "NW"}
    
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


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.GL = QGridLayout()
        self.FeedLabel = QLabel() #object on which the pixelmap will appear in the GUI
        self.GL.addWidget(self.FeedLabel, 0, 0, 2, 1, Qt.AlignCenter)
        self.VideoRetrieve = VideoRetrieve() #create instance of Qthread class
        self.VideoRetrieve.start() #start instance of Qthread class
        self.VideoRetrieve.ImageUpdate.connect(self.ImageUpdateSlot)

        compass = CompassWidget()
        spinBox = QSpinBox()
        spinBox.setRange(0, 359)
        spinBox.valueChanged.connect(compass.setAngle)

        self.GL.addWidget(compass, 0, 1, Qt.AlignCenter)
        self.GL.addWidget(spinBox, 1, 1, Qt.AlignCenter)
        self.setWindowTitle('Nautilus')
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
    def stop(self):
        self.ThreadActive = False
        self.quit()
        self.wait()

    def __init__(self, port=5000):
        super(VideoRetrieve, self).__init__()
        """Summary

        Args:
            port (int, optional): UDP port
        """

        Gst.init(None)

        self.port = port
        self._frame = None

        # [Software component diagram](https://www.ardusub.com/software/components.html)
        # UDP video stream (:5600)
        self.video_source = 'udpsrc port={}'.format(self.port)
        # [Rasp raw image](http://picamera.readthedocs.io/en/release-0.7/recipes2.html#raw-image-capture-yuv-format)
        # Cam -> CSI-2 -> H264 Raw (YUV 4-4-4 (12bits) I420)
        self.video_codec = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        # Python don't have nibble, convert YUV nibbles (4-4-4) to OpenCV standard BGR bytes (8-8-8)
        self.video_decode = \
            '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        # Create a sink to get data
        self.video_sink_conf = \
            '! appsink emit-signals=true sync=false max-buffers=4 drop=true' #D: increase max-buffers to buffer more frames.

        self.video_pipe = None
        self.video_sink = None

        self.begin()

    def start_gst(self, config=None):
        """ Start gstreamer pipeline and sink
        Pipeline description list e.g:
            [
                'videotestsrc ! decodebin', \
                '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                '! appsink'
            ]

        Args:
            config (list, optional): Gstreamer pileline description list
        """

        if not config:
            config = \
                [
                    'videotestsrc ! decodebin',
                    '! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert',
                    '! appsink'
                ]

        command = ' '.join(config)
        self.video_pipe = Gst.parse_launch(command)
        self.video_pipe.set_state(Gst.State.PLAYING)
        self.video_sink = self.video_pipe.get_by_name('appsink0')

    @staticmethod
    def gst_to_opencv(sample):
        """Transform byte array into np array

        Args:
            sample (TYPE): Description

        Returns:
            TYPE: Description
        """
        buf = sample.get_buffer()
        caps = sample.get_caps()
        array = np.ndarray(
            (
                caps.get_structure(0).get_value('height'),
                caps.get_structure(0).get_value('width'),
                3
            ),
            buffer=buf.extract_dup(0, buf.get_size()), dtype=np.uint8)
        return array

    def frame(self):
        """ Get Frame

        Returns:
            iterable: bool and image frame, cap.read() output
        """
        temp = self._frame
        self._frame = None
        return temp

    def frame_available(self):
        """Check if frame is available

        Returns:
            bool: true if frame is available
        """
        return type(self._frame) != type(None)

    def begin(self):
        """ Get frame to update _frame
        """

        self.start_gst(
            [
                self.video_source,
                self.video_codec,
                self.video_decode,
                self.video_sink_conf
            ])

        self.video_sink.connect('new-sample', self.callback)

    def callback(self, sink):
        sample = sink.emit('pull-sample')
        new_frame = self.gst_to_opencv(sample)
        self._frame = new_frame

        return Gst.FlowReturn.OK
    
    def run(self):
        self.ThreadActive = True
        size = (640, 480)
        result = cv2.VideoWriter("DeploymentVideo " + str(datetime.datetime.now()), cv2.VideoWriter_fourcc(*'XVID'),30, size)
        counter = 0
        
        while self.ThreadActive:
            if not self.frame_available():
                continue
            print(counter)
            counter += 1
            frame = self.frame() #capture a frame
            newFrame = cv2.resize(frame, size) #testing resizing
            result.write(newFrame) #maybe have this here?
            Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888) #pass in binary values of the image, converting frame to a QImage
            Pic = ConvertToQtFormat.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation) #suggested 640x480 with Qt.KeepAspectRatio
            self.ImageUpdate.emit(Pic) #emit the QImage
        result.release()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(App.exec())

