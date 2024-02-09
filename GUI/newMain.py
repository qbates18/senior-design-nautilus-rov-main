import sys
from pyQtWidgets import *
import cv2
import gi
import numpy as np
from imports import * #eventually the imports file should be cleaned up...
import datetime

gi.require_version('Gst', '1.0')
from gi.repository import Gst


class MainWindow(QWidget):
    def __init__(self):
        #GUI:
        super(MainWindow, self).__init__()
        self.GL = QGridLayout()
        
        self.bottomWidgetsHorizontalContainer = QHBoxLayout()
        self.GL.addLayout(self.bottomWidgetsHorizontalContainer, 2, 0, 1, 2, Qt.AlignCenter)

        self.movementControlButtonsVerticalContainer = ButtonsVerticalContainers()
        self.bottomWidgetsHorizontalContainer.addLayout(self.movementControlButtonsVerticalContainer, Qt.AlignLeft)

        self.armLocationSelectVerticalContainer = ButtonsVerticalContainers()
        self.bottomWidgetsHorizontalContainer.addLayout(self.armLocationSelectVerticalContainer, Qt.AlignCenter)
        #Widgets:
        self.feedLabel = QLabel() #object on which the pixelmap will appear in the GUI
        self.GL.addWidget(self.feedLabel, 0, 0, 2, 1, Qt.AlignCenter) #add object for camera feed pixelmap to appear on
        
        self.rovArmedButton = RovArmedButton()
        self.movementControlButtonsVerticalContainer.addWidget(self.rovArmedButton, Qt.AlignCenter)

        self.rovSafeModeButton = RovSafeModeButton()
        self.movementControlButtonsVerticalContainer.addWidget(self.rovSafeModeButton, Qt.AlignCenter)
        
        self.moveArmButton = MoveArmButton()
        self.armLocationSelectVerticalContainer.addWidget(self.moveArmButton, Qt.AlignCenter)

        #self.DisplayMessageReceivedTextBox = DisplayMessageReceivedTextBox()
        #self.GL.addWidget(self.DisplayMessageReceivedTextBox, 2, 0, Qt.AlignCenter)
        
        self.compass = CompassWidget()
        self.GL.addWidget(self.compass, 0, 2, 1, 1, Qt.AlignCenter)
        #Threading:
        self.videoRetrieve = VideoRetrieve() #create instance of Qthread class
        self.comms = Comms() #create instance of Qthread class
        self.videoRetrieve.start() #start instance of Qthread class
        self.comms.start() #start instance of Qthread class
        #Slots and Signals
        self.videoRetrieve.ImageUpdate.connect(self.ImageUpdateSlot)
        #self.comms.DisplayMessageReceivedTextBoxUpdate.connect(self.DisplayMessageReceivedTextBox.TextUpdateSlot)
        self.comms.headUpdate.connect(self.compass.setAngle) #slot/signal to connect compass to update function
        #General
        self.setWindowTitle('Nautilus')
        #self.spinBox.setRange(0, 359) #This should be moved to a widget somewhere probably? maybe not if we didn't create a class for it and all functions we need are pre-defined?
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


class Comms(QThread):
    #signals:
    #DisplayMessageReceivedTextBoxUpdate = pyqtSignal(str)
    tmprUpdate = pyqtSignal(str)
    depthUpdate = pyqtSignal(str)
    headUpdate = pyqtSignal(int)
    altitudeUpdate = pyqtSignal(str)
    voltageUpdate = pyqtSignal(str)
    leakUpdate = pyqtSignal(str)
    def __init__(self):
        super(Comms, self).__init__()
        self.threadActive = False
        self.nmea_string = None # This stands for National Marine Electronics Association (NMEA) string protocol
        self.data = None
        self.map_dict = {} # Dictionary for controller 1 for ROV control
        self.map2_dict = {} # Dictionary for controller 2 for arm control
        self.closed_loop_dict={"head" : 0, "depth" : 0, "altitude" : 0}
        self.pid_dict={"head": None, "depth": None, "altitude": None}
        self.gamepad = None
        self.gamepad2 = None
        self.port = '/dev/ttyUSB0' # Should be /dev/ttyUSB0, but every time the FXTI is unpluged and repluged in the it increments by 1 (such as to /dev/ttyUSB1) (more info check README.md)
        self.ard = None # Short for Arduino, this becomes the object which deals with serial communication with the ROV
        self.logFile = None
        #Comms:
        self.arm_value = 1 #should eventually be changed to 0 to be disarmed by default and probably also moved to be associated with the arm/disarm button widget class.
        self.rotationValue = None
        self.tmpr = None
        self.depth = None
        self.head = None
        self.voltage = None
        self.altitude = None
        self.leak = None
        self.startup()
    def stop(self):
        self.threadActive = False
        self.quit()
        self.wait()

    # function: startup()
    # description: called first to initialize components
    def startup(self):
        self.logFile = initialize_log_folder()

        #prepare necessary resources for gamepad
        if config.gamepad_flag:
            print("gamepad initializing...")
            #gamepad initialization
            generate_dictionaries("map.txt") 
            self.gamepad = Gamepad()
            config.gamepad_flag = self.gamepad.init(0) #why are we doing this
            print("gamepad initialized")
        #prepare necessary resources for second gamepad
        if config.gamepad2_flag:
            print("second gamepad initializing...")
            #second gamepad initialization
            generate_dictionaries("map2.txt") 
            self.gamepad2 = Gamepad()
            config.gamepad2_flag = self.gamepad2.init(1)
            print("second gamepad initialized")
            
        # serial initialization 
        if config.serial_flag:
            self.ard = serial.Serial(self.port,115200,timeout=0.2)

    # function: run()
    # description: called to send control strings over serial
    def run(self):
        self.threadActive = True
        while (self.threadActive):
            # listen for gamepad
            if config.gamepad_flag:
                self.gamepad.listen(self.gamepad2)
                interpret(self.gamepad)
                interpret2(self.gamepad2)
                pass
            else:      
                pass

            # Generate string to send subsea
            self.nmea_string = generate(config.top_data, config.sub_data, self.closed_loop_dict, self.pid_dict, self.return_arm(), config.arm_inputs)
            nmea_string_stripped = self.nmea_string.replace(" ", "")

            # Write the generated message to log
            write_to_log(nmea_string_stripped, self.logFile)
            # Encode the string to something that can be handled by serial
            nmea_string_utf = nmea_string_stripped.encode(encoding='ascii')
            if config.serial_flag:
                # Send generated message over serial
                self.ard.write(nmea_string_utf)
                # Wait for message from Arduino to be available, then read it
                receive_string = self.ard.read()
                while("*" not in str(receive_string)): 
                    receive_string += self.ard.read()
                # Parse the message received from the subsea Arduino
                str_receive_string = str(receive_string)
                receive_string_tokens = str_receive_string.split(',', 8)
                initial_token=list(receive_string_tokens[0])
                end_token=list(receive_string_tokens[len(receive_string_tokens)-1])

                #WRITE RECEIVED MESSAGE TO LOG
                write_to_log(str_receive_string, self.logFile)
                #self.DisplayMessageReceivedTextBoxUpdate.emit(str_receive_string)
                # If the recieved message is valid, then update the GUI with new sensor values
                if(initial_token[len(initial_token)-1]=='$' and '*' in end_token and self.validate_receive_string_tokens(receive_string_tokens)):
                    # Read the recieved message for updated values
                    tmpr = receive_string_tokens[2]
                    depth = receive_string_tokens[3]
                    head = receive_string_tokens[4]
                    altitude = receive_string_tokens[5]
                    leak = receive_string_tokens[6]
                    voltage = receive_string_tokens[7]
                    
                    # Add values to the sub_data dictionary to pass to generator
                    # config.sub_data.assign("TMPR", tmpr)
                    # config.sub_data.assign("DEPTH", depth)
                    # config.sub_data.assign("HEAD", head)
                    # config.sub_data.assign("ALT", altitude)

                    # Update graphs wtih new data
                    #^This has been removed for development of PyQt gui as opposed to Tkinter

                    # Update GUI sensor display
                    self.update_sensor_readout(tmpr, depth, head, altitude, voltage, leak)
                    #CLOSED LOOP DICT UPDATE AND PID DICT UPDATE FUNCTIONS ARE COMMENTED OUT TEMPORARILY TO FACILLITATE COMMS INTEGRATION, NEITHER ARE IMPLEMENTED IN NEW CODE
                    #closed_loop_dict = gui.closed_loop_control()
                    #pid_dict = gui.return_pids()   
                    pass
                else:
                    write_to_log("THE PREVIOUS LOG WAS EVALUATED AS INVALID!!", self.logFile)
    
    #function: validate_receive_string_tokens(tokens):
    #description: Ensure that each token received from the arduino is a valid integer or float (depending on the expected data type)
    def validate_receive_string_tokens(self, tokens):
        for token in tokens[1:len(tokens)-1]:
            try:
                float(token)
            except ValueError:
                return False
        return True
    
    #Return true if ROV is armed, false if ROV is disarmed
    def return_arm(self):
        return self.arm_value

    def update_sensor_readout(self, tmpr, depth, head, altitude, voltage, leak):
        #self.rotationValue = self.rotationCounter.calculate_rotation(head)
		#self.rotLbl['text'] = "ROT: " + str(format(self.rotationValue, '.2f'))
        if not tmpr == self.tmpr:
            self.tmprUpdate.emit(str(tmpr))
            self.tmpr = tmpr
        
        if not depth == self.depth:
            self.depthUpdate.emit(str(depth))
            self.depth = depth
        
        head = round(float(head))
        if not head == self.head:
            self.headUpdate.emit(int(head))
            self.head = head
        
        if not altitude == self.altitude:
            self.altitudeUpdate.emit(str(altitude))
            self.altitude = altitude
        
        if not voltage == self.voltage:
            self.voltageUpdate.emit(str(voltage))
            self.voltage = voltage
        
        if not leak == self.leak:
            self.leakUpdate.emit(str(leak))
            self.leak = leak


class VideoRetrieve(QThread):
    ImageUpdate = pyqtSignal(QImage)
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
        size = (1228, 921)
        result = cv2.VideoWriter('/home/rsl/Desktop/NautilusVideoRecordings/Deployment Video ' + str(datetime.datetime.now()), cv2.VideoWriter_fourcc(*'XVID'),16, size)
        framesCounter = 0
        firstStart = True
        while self.ThreadActive:
            if not self.frame_available():
                continue
            if firstStart:
                timeStarted = datetime.datetime.now().timestamp()
                firstStart = False
            framesCounter += 1
            frame = self.frame() #capture a frame
            result.write(cv2.resize(frame, size)) #maybe have this here?
            Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888) #pass in binary values of the image, converting frame to a QImage
            Pic = ConvertToQtFormat.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation) #suggested 640x480 with Qt.KeepAspectRatio
            self.ImageUpdate.emit(Pic) #emit the QImage
        totalTime = datetime.datetime.now().timestamp() - timeStarted
        print("Total time elapsed while receiving camera feed = " + str(totalTime))
        print("Number of Frames received: " + str(framesCounter))
        optimalFps = framesCounter/totalTime
        print("Optimal fps: " + str(optimalFps))
        result.release()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    sys.exit(App.exec())