from pyQtWidgets import QThread, pyqtSignal, QImage, Qt
import numpy as np
import cv2
import datetime
from imports import *

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

class VideoRetrieve(QThread):
    ImageUpdate = pyqtSignal(QImage)
    videoStartSignal = pyqtSignal(datetime)
    def stop(self):
        self.threadActive = False
        self.quit()

    def __init__(self, port=5000):
        super(VideoRetrieve, self).__init__()
        self.threadActive = False
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
        size = (1348, 1011) # (width, height) (1348,1011) Ratio: (1.333333333, 1)
        framesCounter = 0
        firstStart = True
        result = None
        timeVideoStarted = None
        while self.ThreadActive:
            if not self.frame_available():
                continue
            if firstStart:
                result = cv2.VideoWriter('/home/rsl/Desktop/NautilusVideoRecordings/Deployment Video ' + str(timeDeploymentStarted), cv2.VideoWriter_fourcc(*'XVID'),16, size)
                timeVideoStarted = datetime.now()
                self.videoStartSignal.emit(timeVideoStarted)
                firstStart = False
            framesCounter += 1
            frame = self.frame() #capture a frame
            result.write(cv2.resize(frame, size)) #maybe have this here?
            Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888) #pass in binary values of the image, converting frame to a QImage
            Pic = ConvertToQtFormat.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation) #suggested 640x480 with Qt.KeepAspectRatio which takes the width and determines the height based on keeping the aspect ratio with that width
            self.ImageUpdate.emit(Pic) #emit the QImage
        if (timeVideoStarted != None) and (framesCounter != 0):
            totalTime = datetime.now().timestamp() - timeVideoStarted.timestamp()
            print("Total time elapsed while receiving camera feed = " + str(totalTime))
            print("Number of Frames received: " + str(framesCounter))
            print("Optimal fps: " + str(framesCounter/totalTime))
        if result != None:
            result.release()
        print("Request Program Shutdown")
        return
    
    def stopSlot(self):
        self.ThreadActive = False