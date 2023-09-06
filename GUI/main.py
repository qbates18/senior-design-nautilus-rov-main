# file: main.py
# description: main file for GUI
# Nautilus 2021-2022 contributors: Nathan Burke, Mandeep Singh

from imports import *

nmea_string = None #Q: using National Marine Electronics Association (NMEA) string protocol
data = None
map_dict = {} #Q: dictionary for controller 1 (usually the logitech) for ROV control
map2_dict = {} #Q: dictionary for controller 2 (usually the xbox one controller) for arm control
closed_loop_dict={"head" : 0, "depth" : 0, "altitude" : 0}
pid_dict={"head": None, "depth": None, "altitude": None}
gui = None
gamepad = None
gamepad2 = None
port = '/dev/ttyUSB0' #Q: should be /dev/ttyUSB0, but every time the FXTI is unpluged and repluged in the it increments by 1 (such as to /dev/ttyUSB1)
ard = None
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
        config.gamepad_flag = gamepad.init(0)
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

       
    #listen for gamepad
    if config.gamepad_flag:
        gamepad.listen(gamepad2)
        interpret(gamepad)
        interpret2(gamepad2)
        pass
    else:      
        pass

        
    

    nmea_string = generate(config.top_data, config.sub_data, closed_loop_dict, pid_dict, gui.return_arm(), config.arm_inputs)
    #print(nmea_string)
    nmea_string_stripped = nmea_string.replace(" ", "")

    #WRITE SEND MESSAGE TO LOG
    write_to_log(nmea_string_stripped, logFile)

    #print(nmea_string_stripped)
    nmea_string_utf = nmea_string_stripped.encode(encoding='ascii')
    #print(nmea_string_utf)

    if config.serial_flag:
        #send control string over serial
        startTime = time.time() 
        ard.write(nmea_string_utf)
        #print("ard written: ", nmea_string_utf)
        receive_string = ard.read()	
        while("*" not in str(receive_string)): 
            receive_string += ard.read()
            print("waiting")	
        #print("Receive String:", receive_string)
        endTime = time.time()
        #print("time: ", endTime-startTime)
        str_receive_string = str(receive_string)
        receive_string_tokens = str_receive_string.split(',', 8)
        initial_token=list(receive_string_tokens[0])
        end_token=list(receive_string_tokens[len(receive_string_tokens)-1])

        if(initial_token[len(initial_token)-1]=='$' and '*' in end_token): #check if recieved string is valid
            #print("recieved valid string")
            tmpr = receive_string_tokens[2]
            depth = receive_string_tokens[3]
            head = receive_string_tokens[4]
            altitude = receive_string_tokens[5]
            leak = receive_string_tokens[6]
            voltage = receive_string_tokens[7]
            
            #add values coming up from ROV to the sub_data dictionary to pass to generator
            config.sub_data.assign("TMPR", tmpr)
            config.sub_data.assign("DEPTH", depth)
            config.sub_data.assign("HEAD", head)
            config.sub_data.assign("ALT", altitude)

            gui.sensor_display("ALT", altitude)
            gui.sensor_display("DEPTH", depth)
            gui.sensor_display("HEAD", head)
            #gui.rotation_display(head)
            gui.sensor_readout(tmpr, depth, head, altitude, voltage)
            closed_loop_dict = gui.closed_loop_control()
            pid_dict = gui.return_pids()
            #print(pid_dict["depth"].calculate_next(pres))    
            pass
        
            # update camera
            if config.cam_flag:
                cam_update(head, depth)
                pass

            #WRITE RECEIVED MESSAGE TO LOG
            #write_to_log(str_receive_string,logFile) #:Q Why is this commented out?

    

    gui.status_display(nmea_string)
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


# main module to execute functions
if __name__ == "__main__":

    startup()

    #build GUI
    gui = neptuneGUI()
    ani = gui.sensor_animate(config.PROCESS_RATE * 2)

    gui.after(50, processes) #Q: after 50ms run the above recursive processes function which sends and recieves data from arduino and raspi

    gui.protocol("WM_DELETE_WINDOW", on_closing) #Q: when the window is closed run the above on_closeing function
    gui.mainloop() #Q: starts the GUI event handler





