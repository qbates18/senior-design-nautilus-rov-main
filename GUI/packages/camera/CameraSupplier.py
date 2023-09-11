# file: CameraSupplier.py
# description: defines the Camera and Video classes, which populate the camera window with data

import numpy as np
import cv2
from PIL import ImageFont, ImageDraw, Image, ImageColor
import threading
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import queue
import logging  

class Cam:
    colorMode = cv2.COLOR_BGR2RGB
    height = 0
    width = 0

    depthWidth  = 300    # Max recommended:
    compWidth   = 500    # Max recommended:
    maxdepth    = 500

    #r'/home/administrator/Desktop/PySerialGUI2CamUdpdate/packages/camera/consola.ttf'
    #font = ImageFont.truetype("arial.ttf", 30)
    charwidth = 17
    charheight = 25

    def __init__(self):
        self.stream = Video()
        while not self.stream.frame_available():
            continue
        self.frame = self.stream.frame()
        self.page = cv2.cvtColor(self.frame, self.colorMode)
        self.width = self.page.shape[1]
        self.height = self.page.shape[0]
        self.kill_flag = False
        self.HUDStatus = 0
        self.lights = False
        self.headinglock = False
        self.depthlock = False
        self.emergency = False
        self.heading = 0
        self.depth = 0
        self.font = ImageFont.truetype(r'/home/administrator/Desktop/PySerialGUI2CamUdpdate/packages/camera/consola.ttf', 30)

    def drawHUD(self):

        pil_im = Image.new(mode="RGBA", size=(self.width, self.height))
        draw = ImageDraw.Draw(pil_im)

        # Draw compass bar
        compassColor = "white"
        draw.line((self.width / 2 - self.compWidth / 2, 40) + (self.width / 2 + self.compWidth / 2, 40), fill=compassColor, width=3)

        draw.line((self.width / 2 - self.compWidth / 2, 40) + (self.width / 2 - self.compWidth / 2, 0), fill=compassColor, width=3)
        draw.line((self.width / 2 + self.compWidth / 2, 40) + (self.width / 2 + self.compWidth / 2, 0), fill=compassColor, width=3)

        draw.line((self.width / 2, 40) + (self.width / 2, 10), fill=compassColor, width=3)

        draw.line((self.width / 2 - self.compWidth / 4, 40) + (self.width / 2 - self.compWidth / 4, 20), fill=compassColor, width=3)
        draw.line((self.width / 2 + self.compWidth / 4, 40) + (self.width / 2 + self.compWidth / 4, 20), fill=compassColor, width=3)

        draw.line((self.width / 2 - self.compWidth / 8, 40) + (self.width / 2 - self.compWidth / 8, 30), fill=compassColor, width=3)
        draw.line((self.width / 2 + self.compWidth / 8, 40) + (self.width / 2 + self.compWidth / 8, 30), fill=compassColor, width=3)
        draw.line((self.width / 2 - 3 * self.compWidth / 8, 40) + (self.width / 2 - 3 * self.compWidth / 8, 30), fill=compassColor, width=3)
        draw.line((self.width / 2 + 3 * self.compWidth / 8, 40) + (self.width / 2 + 3 * self.compWidth / 8, 30), fill=compassColor, width=3)

        Zero = "0"
        draw.text((self.width / 2 - self.compWidth / 2 - len(Zero) * self.charwidth - 2, 40 - self.charheight / 2), Zero, font=self.font)
        

        CompMax = "359"
        draw.text((self.width / 2 + self.compWidth / 2 + 2, 40 - self.charheight / 2), CompMax, font=self.font)

        draw.rectangle((self.width / 2 - 30, 0) + (self.width / 2 + 30, 30), fill="black", outline="white")
        draw.rectangle((self.width / 2 - 29, 1) + (self.width / 2 + 29, 29), fill="black", outline="white")
        draw.rectangle((self.width / 2 - 28, 2) + (self.width / 2 + 28, 28), fill="black", outline="white")
        
        # Draw depth bar
        depthColor = "white"
        draw.line((40, self.height / 2 - self.depthWidth / 2) + (40, self.height / 2 + self.depthWidth / 2), fill=depthColor, width=3)

        draw.line((40, self.height / 2 - self.depthWidth / 2) + (0, self.height / 2 - self.depthWidth / 2), fill=depthColor, width=3)
        draw.line((40, self.height / 2 + self.depthWidth / 2) + (0, self.height / 2 + self.depthWidth / 2), fill=depthColor, width=3)

        draw.line((40, self.height / 2) + (10, self.height / 2), fill=depthColor, width=3)

        draw.line((40, self.height / 2 - self.depthWidth / 4) + (30, self.height / 2 - self.depthWidth / 4), fill=depthColor, width=3)
        draw.line((40, self.height / 2 + self.depthWidth / 4) + (30, self.height / 2 + self.depthWidth / 4), fill=depthColor, width=3)

        draw.line((40, self.height / 2 - self.depthWidth / 8) + (30, self.height / 2 - self.depthWidth / 8), fill=depthColor, width=3)
        draw.line((40, self.height / 2 + self.depthWidth / 8) + (30, self.height / 2 + self.depthWidth / 8), fill=depthColor, width=3)
        draw.line((40, self.height / 2 - 3 * self.depthWidth / 8) + (30, self.height / 2 - 3 * self.depthWidth / 8), fill=depthColor, width=3)
        draw.line((40, self.height / 2 + 3 * self.depthWidth / 8) + (30, self.height / 2 + 3 * self.depthWidth / 8), fill=depthColor, width=3)

        draw.text((42 , self.height / 2 - self.depthWidth / 2 -self.charheight/2), Zero, font=self.font)

        DepthMax = str(self.maxdepth)
        draw.text((42, self.height / 2 + self.depthWidth / 2 -self.charheight/2), DepthMax, font=self.font)

        draw.rectangle((0, self.height/2 - self.depthWidth/2 - 13) + (60, self.height/2 - self.depthWidth/2 - 45), fill="black", outline="white")
        draw.rectangle((1, self.height/2 - self.depthWidth/2 - 14) + (59, self.height/2 - self.depthWidth/2 - 44), fill="black", outline="white")
        draw.rectangle((2, self.height/2 - self.depthWidth/2 - 15) + (58, self.height/2 - self.depthWidth/2 - 43), fill="black", outline="white")

        return cv2.cvtColor(np.array(pil_im), self.colorMode)

    def drawHUDMove(self,heading, depth):
        pil_im = Image.new(mode="RGBA", size=(self.width, self.height))
        draw = ImageDraw.Draw(pil_im)

        moveColor="yellow"

        # Draw heading
        #Heading = str(heading)
        Heading = "123"
        draw.text((self.width / 2 - len(Heading) * self.charwidth/2, 2), Heading, font=self.font, fill=moveColor)

        # Draw Temp 
        Temperature = "Temp:" + str(37) + "C"
        Temperature = "Temp: 54C"
        draw.text((self.width - len(Temperature) * self.charwidth, self.charheight*1), Temperature, font=self.font,  fill=moveColor)

        # Draw Depth
        Depth = str(depth)
        #Depth = "40ft"
        draw.text((30-len(Depth)*self.charwidth/2,self.height/2 - self.depthWidth/2 - 43), Depth, font=self.font,  fill=moveColor)

        # Draw compass heading bar
        headingPercent = self.compWidth * (float(heading) / 360)
        draw.line((self.width / 2 - self.compWidth / 2 + headingPercent, 30) + (self.width / 2 - self.compWidth / 2 + headingPercent, 60),
                  fill=moveColor, width=3)

        # draw depth level bar
        depthPercent = self.depthWidth * (float(depth) / self.maxdepth)
        draw.line((20, self.height / 2 - self.depthWidth / 2 + depthPercent) + (60, self.height / 2 - self.depthWidth / 2 + depthPercent),
                  fill=moveColor, width=3)

        return cv2.cvtColor(np.array(pil_im),  self.colorMode)

    def drawHUDStatus(self, lights, headinglock, depthlock, emergency):
        pil_im = Image.new(mode="RGBA", size=(self.width, self.height))
        draw = ImageDraw.Draw(pil_im)

        events = 1
        if lights:
            Lights = "LGHT ACT"
            draw.text((self.width - len(Lights) * self.charwidth, self.height - events * self.charheight), Lights, font=self.font)
            events = events + 1
        if headinglock:
            HeadLock = "HDNG LCK"
            draw.text((self.width - len(HeadLock) * self.charwidth, self.height - events * self.charheight), HeadLock, font=self.font)
            events = events + 1
        if depthlock:
            DepthLock = "DPTH LCK"
            draw.text((self.width - len(DepthLock) * self.charwidth, self.height - events * self.charheight), DepthLock, font=self.font)
            events = events + 1
        if emergency:
            Emrg = "EMRG SIG"
            draw.rectangle((self.width / 2 - (len(Emrg) * self.charwidth) / 2 - 2, self.height - 42) + (self.width / 2 + (len(Emrg) * self.charwidth) / 2 + 2, self.height - 38 + self.charheight), fill="black", outline="white")
            draw.rectangle((self.width / 2 - (len(Emrg) * self.charwidth) / 2 - 1, self.height - 41) + (self.width / 2 + (len(Emrg) * self.charwidth) / 2 + 1, self.height - 39 + self.charheight), fill="black", outline="white")
            draw.rectangle((self.width / 2 - (len(Emrg) * self.charwidth) / 2    , self.height - 40) + (self.width / 2 + (len(Emrg) * self.charwidth) / 2    , self.height - 40 + self.charheight), fill="black", outline="white")
            draw.text((self.width / 2 - (len(Emrg) * self.charwidth) / 2, self.height - 40), Emrg, font=self.font)
            events = events + 1
        return cv2.cvtColor(np.array(pil_im), self.colorMode)

    def update(self):
        print('from_thread')
        hudStatic = self.drawHUD()
        # hudmask = cv2.cvtColor(hudStatic, cv2.COLOR_BGR2GRAY)
        # hudinv = cv2.bitwise_not(hudmask)
        # hudinv = cv2.cvtColor(hudinv, cv2.COLOR_BGR2RGB)

        self.HUDStatus = self.drawHUDStatus(self.lights, self.headinglock, self.depthlock, self.emergency)

        
        while True:
            self.heading = (float(self.heading) + 1) % 360
            self.depth = (float(self.depth) + 1) % 500

            if not self.stream.frame_available():
                continue
            
            cam = self.stream.frame()

            composition = cv2.bitwise_or(cam, hudStatic)
            #composition = cv2.bitwise_or(composition,self.drawHUDMove(self.heading, self.depth))
            #composition = cv2.bitwise_or(composition, self.HUDStatus)

            self.page = composition
            #self.page = cam
            
            cv2.imshow('frame', self.page)
            #logging.critical(self.page)
            #logging.critical("width: %s", self.width)
            #logging.critical("height: %s", self.height)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            if self.kill_flag:
                break

    def start(self):
        # start the thread to read frames from the video stream
        print('start')
        threading.Thread(target=self.update, args=()).start()
        return self

    def read(self):
        #return self.stream.frame()
        return self.page

    def updateLights(self, signal):
        self.lights = signal
        self.HUDStatus = self.drawHUDStatus(self.lights, self.headinglock, self.depthlock, self.emergency)

    def updateHeadingLock(self, signal):
        self.headinglock = signal
        self.HUDStatus = self.drawHUDStatus(self.lights, self.headinglock, self.depthlock, self.emergency)

    def updateDepthLock(self, signal):
        self.depthlock = signal
        self.HUDStatus = self.drawHUDStatus(self.lights, self.headinglock, self.depthlock, self.emergency)

    def updateEmergencySignal(self, signal):
        self.emergency = signal
        self.HUDStatus = self.drawHUDStatus(self.lights, self.headinglock, self.depthlock, self.emergency)

    def updateHeading(self, signal):
        self.heading = signal

    def updateDepth(self, signal):
        self.depth = signal

    def vssTest(self):
        print('VSS THING')

    def kill(self):
        self.kill_flag = True

class Video():
    def __init__(self, port=5000):
        Gst.init(None)
        self.port = port
        self._frame = None
        self.video_source = 'udpsrc port={}'.format(self.port)
        self.video_codec = '! application/x-rtp, payload=96 ! rtph264depay ! h264parse ! avdec_h264'
        self.video_decode = '! decodebin ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert'
        self.video_sink_conf = '! appsink emit-signals=true sync=false max-buffers=2 drop=true'
        self.video_pipe = None
        self.video_sink = None
        
        self.run()

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
        #print(caps.get_structure(0).get_value('height')) 
        return array

    def frame(self):
        """ Get Frame

        Returns:
            iterable: bool and image frame, cap.read() output
        """
        return self._frame

    def frame_available(self):
        """Check if frame is available

        Returns:
            bool: true if frame is available
        """
        return type(self._frame) != type(None)

    def run(self):
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
