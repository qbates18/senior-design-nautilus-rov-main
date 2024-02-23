from imports import *
from pyQtWidgets import QThread, pyqtSignal

class Comms(QThread):
    #signals:
    #DisplayMessageReceivedTextBoxUpdate = pyqtSignal(str)
    temperatureUpdate = pyqtSignal(str)
    depthUpdate = pyqtSignal(float)
    headUpdate = pyqtSignal(int)
    altitudeUpdate = pyqtSignal(float)
    voltageUpdate = pyqtSignal(float)
    leakUpdate = pyqtSignal(int)
    armUpdate = pyqtSignal(bool)
    headingLockValueUpdate = pyqtSignal(int)
    depthLockValueUpdate = pyqtSignal(float)
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
        self.arm_value = 0
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
            self.nmea_string = generate(config.top_data, config.sub_data, self.closed_loop_dict, self.pid_dict, self.get_arm(), config.arm_inputs)
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
                if not self.threadActive:
                    break
                # Parse the message received from the subsea Arduino
                str_receive_string = str(receive_string)
                if ("&" in str_receive_string):#if the string received has an '&' at the end (i.e. it is an error sent up from the arduino, perhaps because it is unable to initialize one of the sensors or something)
                    print("\nError Received From Arduino!\n" + str_receive_string + "\n") #print the message
                else:
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
        print("Request Video Shutdown")
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

    def update_sensor_readout(self, tmpr, depth, head, altitude, voltage, leak):
        #self.rotationValue = self.rotationCounter.calculate_rotation(head)
		#self.rotLbl['text'] = "ROT: " + str(format(self.rotationValue, '.2f'))
        if not tmpr == self.tmpr:
            self.temperatureUpdate.emit(str(tmpr))
            self.tmpr = tmpr
        
        depth = round(float(depth), 1)
        if not depth == self.depth:
            self.depthUpdate.emit(depth)
            self.depth = depth
        
        head = round((float(head)+config.heading_offset) % 360)
        if not head == self.head:
            self.headUpdate.emit(int(head))
            self.head = head
        
        altitude = round(float(altitude))
        if not altitude == self.altitude:
            self.altitudeUpdate.emit(altitude)
            self.altitude = altitude
        
        if not voltage == self.voltage:
            self.voltageUpdate.emit(float(voltage))
            self.voltage = voltage
        
        if not leak == self.leak:
            self.leakUpdate.emit(int(float(leak[1:]))) #get rid of leading space, cast to float, cast to int, emit int
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
                    print("Invalid heading value provided!")
                    return
                desiredHeading = int(desiredHeading) % 360
                self.closed_loop_dict["head"] = 1
                self.pid_dict["head"] = head_PID(desiredHeading)
                print("HEADING LOCK SET USING TEXT BOX TO: " + str(desiredHeading))
            else:
                self.closed_loop_dict["head"] = 1
                self.pid_dict["head"] = head_PID(self.head)
                print("HEADING LOCK SET USING CURRENT HEADING TO: " + str(self.head))
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
                    print("Invalid depth value provided!")
                    return
                desiredDepth = float(desiredDepth)
                self.closed_loop_dict["depth"] = 1
                self.pid_dict["depth"] = depth_PID(desiredDepth)
                print("DEPTH LOCK SET USING TEXT BOX TO: " + str(desiredDepth))
            else:
                self.closed_loop_dict["depth"] = 1
                self.pid_dict["depth"] = depth_PID(self.depth)
                print("DEPTH LOCK SET USING CURRENT DEPTH TO: " + str(self.depth))
        self.depthLockValueUpdate.emit(int(self.pid_dict["depth"].getDesiredValue()) if self.pid_dict["depth"] != None else -1) #-1 indicates depth lock has been turned off

    def stopSlot(self):
        self.threadActive = False