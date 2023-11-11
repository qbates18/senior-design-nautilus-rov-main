# file: main.py
# description: main file for GUI
# Nautilus 2021-2022 contributors: Nathan Burke, Mandeep Singh

from imports import *

nmea_string = None # This stands for National Marine Electronics Association (NMEA) string protocol
data = None
map_dict = {} # Dictionary for controller 1 for ROV control
map2_dict = {} # Dictionary for controller 2 for arm control
closed_loop_dict={"head" : 0, "depth" : 0, "altitude" : 0}
pid_dict={"head": None, "depth": None, "altitude": None}
gui = None
gamepad = None
gamepad2 = None
port = '/dev/ttyUSB0' # Should be /dev/ttyUSB0, but every time the FXTI is unpluged and repluged in the it increments by 1 (such as to /dev/ttyUSB1) (more info check README.md)
ard = None # Short for Arduino, this becomes the object which deals with serial communication with the ROV
logFile = None


# function: startup()
# description: called first to initialize components
def startup():
    global ard, logFile    

    logFile = initialize_log_folder()

    #prepare necessary resources for gamepad
    if config.gamepad_flag:
        global gamepad
        print("gamepad initializing...")
        #gamepad initialization
        generate_dictionaries("map.txt") 
        gamepad = Gamepad()
        config.gamepad_flag = gamepad.init(0) #why are we doing this
        print("gamepad initialized")
    #prepare necessary resources for second gamepad
    if config.gamepad2_flag:
        global gamepad2
        print("second gamepad initializing...")
        #second gamepad initialization
        generate_dictionaries("map2.txt") 
        gamepad2 = Gamepad()
        config.gamepad2_flag = gamepad2.init(1)
        print("second gamepad initialized")
    	
    # serial initialization 
    if config.serial_flag:
        ard = serial.Serial(port,115200,timeout=0.2)
    
    # camera initialization
    if config.cam_flag:
        cam_init()

    # if config.altitude_lock_flag:
    #     init_altitude_pid(20)


# function: processes()
# description: called to send control strings over serial
# and update GUI overlay video and data
def processes():
    global nmea_string, gamepad, gamepad2, ard, closed_loop_dict, pid_dict, logFile 

    # listen for gamepad
    if config.gamepad_flag:
        gamepad.listen(gamepad2)
        interpret(gamepad)
        interpret2(gamepad2)
        pass
    else:      
        pass

    # Generate string to send subsea
    nmea_string = generate(config.top_data, config.sub_data, closed_loop_dict, pid_dict, gui.return_arm(), config.arm_inputs)
    nmea_string_stripped = nmea_string.replace(" ", "")

    # Write the generated message to log
    write_to_log(nmea_string_stripped, logFile)

    # Encode the string to something that can be handled by serial
    nmea_string_utf = nmea_string_stripped.encode(encoding='ascii')

    #Set heading to the value of the previous heading. This will be overwritten with the new heading value only if it is able to be interpreted as a float.
    # head = prevHead

    if config.serial_flag:
        # Send generated message over serial
        ard.write(nmea_string_utf)

        # Wait for message from Arduino to be available, then read it
        receive_string = ard.read()	
        while("*" not in str(receive_string)): 
            receive_string += ard.read()

        # Parse the message received from the subsea Arduino
        str_receive_string = str(receive_string)
        receive_string_tokens = str_receive_string.split(',', 8)
        initial_token=list(receive_string_tokens[0])
        end_token=list(receive_string_tokens[len(receive_string_tokens)-1])

        #WRITE RECEIVED MESSAGE TO LOG
        write_to_log(str_receive_string,logFile)
        
        # If the recieved message is valid, then update the GUI with new sensor values
        if(initial_token[len(initial_token)-1]=='$' and '*' in end_token and validate_receive_string_tokens(receive_string_tokens)):
            # Read the recieved message for updated values
            tmpr = receive_string_tokens[2]
            depth = receive_string_tokens[3]
            head = receive_string_tokens[4]
            altitude = receive_string_tokens[5]
            leak = receive_string_tokens[6]
            voltage = receive_string_tokens[7]
            
            # Add values to the sub_data dictionary to pass to generator
            config.sub_data.assign("TMPR", tmpr)
            config.sub_data.assign("DEPTH", depth)
            config.sub_data.assign("HEAD", head)
            config.sub_data.assign("ALT", altitude)

            # Update graphs wtih new data
            gui.sensor_display("ALT", altitude)
            gui.sensor_display("DEPTH", depth)
            gui.sensor_display("HEAD", head)

            # Update GUI sensor display
            #check that head is valid if yes do the next line if no don't
            gui.sensor_readout(tmpr, depth, head, altitude, voltage)
            closed_loop_dict = gui.closed_loop_control()
            pid_dict = gui.return_pids()   
            pass
        
            # update camera
            if config.cam_flag:
                cam_update(head, depth)
                pass
        else:
            write_to_log("THE PREVIOUS LOG WAS EVALUATED AS INVALID!!", logFile)

            

    
    # Display generated message at the bottom of the GUI
    gui.status_display(nmea_string)

    # Call this function again, after the amount of time set in config.py
    gui.after(config.PROCESS_RATE, processes)


# function: on_closing()
# description: called on exit to kill camera and GUI processes
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if config.gamepad_flag:
            pass
        
        if config.serial_flag:
            pass

        if config.cam_flag:
            cam_kill()
            pass
            
        gui.destroy()

#function: validate_receive_string_tokens(tokens):
#description: Ensure that each token received from the arduino is a valid integer or float (depending on the expected data type)
def validate_receive_string_tokens(tokens):
    for token in tokens[1:len(tokens)-1]:
        try:
            float(token)
        except ValueError:
            return False
    return True

# function: main()
# description: main module to execute functions
if __name__ == "__main__":

    startup()

    # build GUI
    gui = neptuneGUI()
    ani = gui.sensor_animate(config.PROCESS_RATE * 2) 

    gui.after(50, processes) #Q: after 50ms run the above recursive processes function which sends and recieves data from arduino and raspi

    gui.protocol("WM_DELETE_WINDOW", on_closing) # when the window is closed run the above on_closeing function
    
    # Start the GUI event handler
    gui.mainloop() 



