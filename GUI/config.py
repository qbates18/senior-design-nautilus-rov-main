# file: config.py  
# description: set parameters and enable/disable functionality based on the current hardware configuration

from packages.models.input import Data
import datetime
timeDeploymentStarted = datetime.datetime.now() #universal source of truth for the start time of the deployment

CAM_RATE = 1
INPUT_RATE = 500
PROCESS_RATE = 100

THRESHOLD = 0.1 # sets controller deadzone: the minimal joystick input value required for manuvering thruster motion

gamepad_flag = True
gamepad2_flag = True
cam_flag = False #Q: is this used anymore? D: No?
serial_flag = True
altitude_lock_flag = False
endpoint_control_flag = False

top_data = Data(["FORWARD", "RIGHT", "BACK", "LEFT", "DOWN", "UP", "ROT_CCW", "ROT_CW", "S_TOG", "L_TOG", "CAM_UP", "CAM_DN"])
sub_data = Data(["TMPR", "DEPTH", "HEAD", "ALT", "VOLT", "ROT", "LEAK", "SAFE", "ARM"])

arm_inputs = Data(["S1_LEFT", "S1_RIGHT", "S2_FORWARD", "S2_BACK", "S3_LEFT", "S3_RIGHT", "S4_OPEN", "S4_CLOSE", "S5_CW", "S5_CCW", "theta1", "theta2", "theta3"])

map_dict = None
map2_dict = None

heading_offset = 324
NAUTILUS_MAX_RATED_DEPTH = 100 #100 as of April 2024
NAUTILUS_SAFE_DEPTH = 0.9 # percentage (of 1) that the safe mode should toggle at and depth warning indicator should turn red at (it will turn orange at NAUTILUS_MAX_RATED_DEPTH * NAUTILUS_SAFE_DEPTH * 0.9)

defaultPidGainsValuesDict = {"Heading Kp": 2,
                             "Heading Ki": 0.2,
                             "Heading Kd": 0.0,
                             "Depth Kp": 75,
                             "Depth Ki": 2,
                             "Depth Kd": 0,
                             "Altitude Kp": 75,
                             "Altitude Ki": 2,
                             "Altitude Kd": 10}

# Placeholder values until further testing is done meant to represent values for the arm servos
armLocationsDict = {"Travel Home": (0, 0, 0),
                    "Workspace Home": (1, 0, 0),
                    "Storage 1": (2, 1, 0),
                    "Storage 2": (2, 2, 0),
                    "Storage 3": (2, 3, 0)}

VideoSize = (1324, 993) # (width, height) (1348,1011) for Wayland and (1324, 993) for X11 Ratio: (1.333333333, 1)

dateToday = datetime.date.today()
captainLogFolderString = '/home/rsl/Desktop/NautilusCaptain\'sLogs/Captain\'sLog ' + str(dateToday)
captainLogFileName = captainLogFolderString + "/" +str(timeDeploymentStarted)