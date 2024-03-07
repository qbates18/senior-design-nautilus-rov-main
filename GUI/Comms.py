from imports import *
from pyQtWidgets import QThread, pyqtSignal

class Comms(QThread):
    #signals:
    #DisplayMessageReceivedTextBoxUpdate = pyqtSignal(str)
    temperatureUpdate = pyqtSignal(float)
    depthUpdate = pyqtSignal(float)
    headUpdate = pyqtSignal(int)
    altitudeUpdate = pyqtSignal(float)
    voltageUpdate = pyqtSignal(float)
    leakUpdate = pyqtSignal(int)
    armUpdate = pyqtSignal(bool)
    safemodeUpdate = pyqtSignal(bool)
    headingLockValueUpdate = pyqtSignal(int)
    depthLockValueUpdate = pyqtSignal(float)
    commsStatusUpdate = pyqtSignal(bool)
    addArduinoErrorMessageUpdate = pyqtSignal(str)
    def __init__(self):
        super(Comms, self).__init__()
        self.threadActive = False
        self.nmea_string = None # This stands for National Marine Electronics Association (NMEA) string protocol
        self.data = None
        self.map_dict = {} # Dictionary for controller 1 for ROV control
        self.map2_dict = {} # Dictionary for controller 2 for arm control
        self.closed_loop_dict={"head" : 0, "depth" : 0, "altitude" : 0}
        self.pid_dict={"head": None, "depth": None, "altitude": None}
        self.pidGainsValuesDict = config.defaultPidGainsValuesDict
        self.safemode = True
        self.gamepad = None
        self.gamepad2 = None
        self.port = '/dev/ttyUSB0' # Should be /dev/ttyUSB0, but every time the FXTI is unpluged and repluged in the it increments by 1 (such as to /dev/ttyUSB1) (more info check README.md)
        self.ard = None # Short for Arduino, this becomes the object which deals with serial communication with the ROV
        self.logFile = None
        #Comms:
        self.arm_value = 0
        self.rotationValue = 0
        self.tmpr = 0
        self.depth = 0
        self.head = 0
        self.voltage = None #leave as none to prevent critical battery warning on startup
        self.altitude = 0
        self.leak = 0
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
            #gamepad initialization
            generate_dictionaries("map.txt") 
            self.gamepad = Gamepad()
            config.gamepad_flag = self.gamepad.init(0) #why are we doing this
        #prepare necessary resources for second gamepad
        if config.gamepad2_flag:
            #second gamepad initialization
            generate_dictionaries("map2.txt") 
            self.gamepad2 = Gamepad()
            config.gamepad2_flag = self.gamepad2.init(1)
            
        # serial initialization 
        if config.serial_flag:
            self.ard = serial.Serial(self.port,115200,timeout=0.2)

    # function: run()
    # description: called to send control strings over serial
    def run(self):
        self.threadActive = True
        lastSuccessfulMessage = 0
        commsStatusGood = False
        while (self.threadActive):
            # listen for gamepad
            if config.gamepad_flag:
                self.gamepad.listen(self.gamepad2)
                interpret(self.gamepad)
                interpret2(self.gamepad2)

            # Generate string to send subsea
            self.nmea_string = generate(config.top_data, config.sub_data, self.closed_loop_dict, self.pid_dict, self.safemode, self.depth, self.get_arm(), config.arm_inputs)
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
                while(("*" not in str(receive_string)) and ("&" not in str(receive_string)) and self.threadActive): 
                    receive_string += self.ard.read()
                    if commsStatusGood:
                        if datetime.now().timestamp() - lastSuccessfulMessage > 1: #if have been waiting in this loop for one second or more, emit signal that comms has been lost
                            commsStatusGood = False
                            self.commsStatusUpdate.emit(commsStatusGood)
                if not self.threadActive:
                    break
                lastSuccessfulMessage = datetime.now().timestamp()
                if not commsStatusGood:
                    commsStatusGood = True
                    self.commsStatusUpdate.emit(commsStatusGood)
                    self.leakUpdate.emit(self.leak)
                    if self.voltage != None: self.voltageUpdate.emit(self.voltage)
                    self.depthUpdate.emit(self.depth)
                    

                # Parse the message received from the subsea Arduino
                str_receive_string = str(receive_string)
                if ("&" in str_receive_string):#if the string received has an '&' at the end (i.e. it is an error sent up from the arduino, perhaps because it is unable to initialize one of the sensors or something)
                    self.addArduinoErrorMessageUpdate.emit(str_receive_string)
                else:
                    receive_string_tokens = str_receive_string.split(',', 8)
                    initial_token=list(receive_string_tokens[0])
                    end_token=list(receive_string_tokens[len(receive_string_tokens)-1])

                    #WRITE RECEIVED MESSAGE TO LOG
                    write_to_log(str_receive_string, self.logFile)
                    
                    # If the recieved message is valid, then update the GUI with new sensor values
                    if(initial_token[len(initial_token)-1]=='$' and '*' in end_token and self.validate_receive_string_tokens(receive_string_tokens)):
                        # Read the recieved message for updated values
                        tmpr = receive_string_tokens[2]
                        depth = receive_string_tokens[3]
                        head = receive_string_tokens[4]
                        altitude = receive_string_tokens[5]
                        leak = receive_string_tokens[6]
                        voltage = receive_string_tokens[7]

                        self.update_sensor_readout(tmpr, depth, head, altitude, voltage, leak)
                    else:
                        write_to_log("THE PREVIOUS LOG WAS EVALUATED AS INVALID!!", self.logFile)
        return    
    #function: validate_receive_string_tokens(tokens):
    #description: Ensure that each token received from the arduino is a valid integer or float (depending on the expected data type)
    def validate_receive_string_tokens(self, tokens):
        for token in tokens[1:len(tokens)-1]:
            try:
                float(token)
            except ValueError:
                return False
        return True
    #function: update_sensor_readout(self, tmpr, depth, head, altitude, voltage, leak):
    #description: round (if desired) and then emit the value if it is new (i.e. different from self.value).
    def update_sensor_readout(self, tmpr, depth, head, altitude, voltage, leak):
        tmpr = round(float(tmpr), 1)
        if not tmpr == self.tmpr:
            self.temperatureUpdate.emit(tmpr)
            self.tmpr = tmpr
        
        depth = round(float(depth), 1)
        if not depth == self.depth:
            self.depthUpdate.emit(depth)
            self.depth = depth
        
        head = int(round((float(head)+config.heading_offset) % 360))
        if not head == self.head:
            self.headUpdate.emit(head)
            self.head = head
        
        altitude = round(float(altitude), 1)
        if not altitude == self.altitude:
            self.altitudeUpdate.emit(altitude)
            self.altitude = altitude
        
        voltage = round(float(voltage), 1)
        if not voltage == self.voltage:
            self.voltageUpdate.emit(voltage)
            self.voltage = voltage
        
        if not leak == self.leak:
            leak = int(float(leak[1:])) #get rid of leading space, cast to float (because it's a string in the form of "x.xx"), cast to int, emit int. this is because leak comes from the string received from the arduino as a string of the form "1.00" you can't int that kind of string but you can float it, and then you can int the float.
            self.leakUpdate.emit(leak)
            self.leak = leak
    def getHeading(self):
        return self.head
    def getVoltage(self):
        return self.voltage
    def getAltitude(self):
        return self.altitude
    def getDepth(self):
        return self.depth
    def getTemperature(self):
        return self.tmpr
    def getLeak(self):
        return self.leak
    def getRotation(self):
        return self.rotationValue
    #Return true if ROV is armed, false if ROV is disarmed
    def get_arm(self):
        return self.arm_value
    def armRovSlot(self):
        self.arm_value = 0 if self.arm_value else 1 #take care that arm_value isn't turned into a bool because generator.py assumes it to be an int
        self.armUpdate.emit(self.arm_value)
    def safemodeSlot(self):
        self.safemode = not self.safemode
        self.safemodeUpdate.emit(self.safemode)
        print("comms just emitted, safe mode is: " + str(self.safemode))
    def setHeadingLockSlot(self, desiredHeading):
        if (self.closed_loop_dict["head"]):
            self.closed_loop_dict["head"] = 0
            self.pid_dict["head"] = None
        else:
            if (desiredHeading != ""):
                match desiredHeading:
                    case "N":
                        desiredHeading = 0
                    case "NE":
                        desiredHeading = 45
                    case "E":
                        desiredHeading = 90
                    case "SE":
                        desiredHeading = 135
                    case "S":
                        desiredHeading = 180
                    case "SW":
                        desiredHeading = 225
                    case "W":
                        desiredHeading = 270
                    case "NW":
                        desiredHeading = 315
                try:
                    int(desiredHeading)
                except:
                    ValueError
                    return
                desiredHeading = int(desiredHeading) % 360
                self.closed_loop_dict["head"] = 1
                self.pid_dict["head"] = head_PID(desiredHeading,
                                                 self.pidGainsValuesDict["Heading Kp"],
                                                 self.pidGainsValuesDict["Heading Ki"],
                                                 self.pidGainsValuesDict["Heading Kd"])
            else:
                self.closed_loop_dict["head"] = 1
                self.pid_dict["head"] = head_PID(self.head,
                                                 self.pidGainsValuesDict["Heading Kp"],
                                                 self.pidGainsValuesDict["Heading Ki"],
                                                 self.pidGainsValuesDict["Heading Kd"])
        self.headingLockValueUpdate.emit(int(self.pid_dict["head"].getDesiredValue()) if self.pid_dict["head"] != None else -1) #-1 indicates heading lock has been turned off
    def setDepthLockSlot(self, desiredDepth):
        if (self.closed_loop_dict["depth"]):
            self.closed_loop_dict["depth"] = 0
            self.pid_dict["depth"] = None
        else:
            if (desiredDepth != ""):
                try:
                    float(desiredDepth)
                except:
                    ValueError
                    return
                desiredDepth = float(desiredDepth)
                self.closed_loop_dict["depth"] = 1
                self.pid_dict["depth"] = depth_PID(desiredDepth,
                                                   self.pidGainsValuesDict["Depth Kp"],
                                                   self.pidGainsValuesDict["Depth Ki"],
                                                   self.pidGainsValuesDict["Depth Kd"])
            else:
                self.closed_loop_dict["depth"] = 1
                self.pid_dict["depth"] = depth_PID(self.depth,
                                                   self.pidGainsValuesDict["Depth Kp"],
                                                   self.pidGainsValuesDict["Depth Ki"],
                                                   self.pidGainsValuesDict["Depth Kd"])
        self.depthLockValueUpdate.emit(float(self.pid_dict["depth"].getDesiredValue()) if self.pid_dict["depth"] != None else -1) #-1 indicates depth lock has been turned off
    
    def devToolsItemsDictUpdateSlot(self, devToolsDict):
        self.pidGainsValuesDict = devToolsDict

    def stopSlot(self):
        self.threadActive = False