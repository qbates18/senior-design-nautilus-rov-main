# file: generator.py
# description: file used to generate the message passed down to the ROV (topside -> subsea)

import string
import time
import math

import config
from imports import *
from packages.closed_loop.PIDs import *

ack_id = 0 

l_tog_flag = False
s_tog_flag = False

s1_mapped = 205 #going lower makes it move away from robot
s2_mapped = 190 #going lower makes it go higher
s3_mapped = 205 #going lower makes it arc from right to left
s4_mapped = 210 #going lower makes it open more
s5_mapped = 0



# function: generate()
# description: generate a message to send commands to the ROV using the National Marine Electronics Association (NMEA) string protocol
def generate(input, subData, closed_loop_dict, pid_dict, safemode, depth, arm_disarm_value, arm_inputs):
	global ack_id
	global l_tog_flag
	global s_tog_flag
	global s1_mapped, s2_mapped, s3_mapped, s4_mapped, s5_mapped  
	

	temp_pres = subData.read("PRES")
	temp_tmpr = subData.read("TMPR")
	temp_alt = subData.read("ALT")
	temp_head = subData.read("HEAD")

	# ------ Token1: Start of string ------
	output =  "$"

	# ------ Token2: Message id ------
	output = add_next(output, str(ack_id))
	ack_id = ack_id + 1

	# ------ Token3 and Token4: Controller1 Left Joystick XY values for Maneuvering Thrusters Direcitonal Motion ------
	x = min(input.read("RIGHT") - input.read("LEFT"), 1)
	y = min(input.read("FORWARD") - input.read("BACK"), 1)
	output = add_next(output, str(x))
	output = add_next(output, str(y))

	# ------ Token5: Controller1 Trigger values for Vertical Thrusters ------
	# If neither depth and altitude locks are enabled then calculate verticals normally
	if closed_loop_dict["depth"] == 0 and closed_loop_dict["altitude"] == 0:
		# takes analog value from 0 to 1 for each up and down
		if input.read("UP") > 0 and input.read("DOWN") == 0:
			output = add_next(output, str(format(input.read("UP"), '.3f')))
		elif input.read("UP") == 0 and input.read("DOWN") < 0:
			# If safe mode is on and the current depth is dangerous
			if safemode == True and depth > config.NAUTILUS_MAX_RATED_DEPTH * config.NAUTILUS_SAFE_DEPTH: # current depth dangerous, also implied that depth lock is off and controls are going down
				output = add_next(output, str(format(0, '.3f'))) # do nothing?
			else:
				output = add_next(output, str(format(input.read("DOWN"), '.3f')))
		else:
			output = add_next(output, str(format(0, '.3f')))
	# If the altitude lock is enabled use altitude closed loop control
	elif closed_loop_dict["depth"] == 0 and closed_loop_dict["altitude"] == 1:
		output = add_next(output, str(format(pid_dict["altitude"].calculate_next(temp_alt), '.3f'))) 
	# If depth lock is enabled use depth closed loop control
	elif closed_loop_dict["depth"] == 1 and closed_loop_dict["altitude"] == 0:
		output = add_next(output, str(format(pid_dict["depth"].calculate_next(temp_pres), '.3f'))) 
	else:
		output = add_next(output, str(format(0, '.3f')))
	

	# ------ Token6: Controller1 Right Joystick Horizontal values for Manuvering Thruster Rotational Motion ------
	# If 0 closed loop heading control is off, if 1 then its on, otherwise default to off
	if closed_loop_dict["head"] == 0:
		if input.read("ROT_CW") > config.THRESHOLD and input.read("ROT_CCW") == 0:
			output = add_next(output, str(format(input.read("ROT_CW"), '.3f')))
		elif input.read("ROT_CW") == 0 and input.read("ROT_CCW") > config.THRESHOLD:
			output = add_next(output, str(format(-input.read("ROT_CCW"), '.3f')))
		else:
			output = add_next(output, str(format(0, '.3f')))
	# If heading lock is enabled
	elif closed_loop_dict["head"] == 1:
		output = add_next(output, str(format(pid_dict["head"].calculate_next(temp_head), '.3f')))
	else:
		output = add_next(output, str(format(0, '.3f')))


	# ------ Token7: Controller1 "Y" Button for Toggling Lights ------
	if input.read("L_TOG") == 1 and l_tog_flag == False:
		output = add_next(output, 'T')
		l_tog_flag = True
	elif input.read("L_TOG") == 0:
		output = add_next(output, 'F')
		l_tog_flag = False
	elif input.read("L_TOG") == 1 and l_tog_flag == True:
		output = add_next(output, 'F')
	else:
		output = add_next(output, 'E')

	# ------ Token8: Controller1 "B" Button for Toggling Sampler ------
	if input.read("S_TOG") == 1 and s_tog_flag == False:
		output = add_next(output, 'T')
		s_tog_flag = True
	elif input.read("S_TOG") == 0:
		output = add_next(output, 'F')
		s_tog_flag = False
	elif input.read("S_TOG") == 1 and s_tog_flag == True:
		output = add_next(output, 'F')
	else:
		output = add_next(output, 'E')

	# ------ Token9: Controller1 DPad Up/Down for Tilting Camera Servo ------
	if input.read("CAM_UP") == 1 and input.read("CAM_DN") == 0:
		output = add_next(output, 'U')
	elif input.read("CAM_UP") == 0 and input.read("CAM_DN") == 1:
		output = add_next(output, 'D')
	else:
		output = add_next(output, 'S')

	# ------ Token10: GUI Arm/Disarm Value for ROV Motion ------
	output = add_next(output, str(arm_disarm_value))
	

	# ------ Token11-15: Controller2 Robotic Manipulator Joint Servo Values ------
	# reads controller values and maps them to pwm values for servos
	# robot arm servo controller pins 0,2,12,14,15 from left to right servo1-servo5
	
	mult = 30 # movement multiplier, increase mult to increase servo speed

	# If endpoint control is enabled, set servo values accordingly
	if(endpoint_control_flag):

		s1_mapped += arm_inputs.read("theta1")
		if (s1_mapped < 100):
			s1_mapped = 100
		elif (s1_mapped > 310):
			s1_mapped = 310

		servo2 = 0 #currently set to 0 because it has not been tested/made to work yet
		if (s2_mapped > 100 or s2_mapped < 310): 
			s2_mapped +=(servo2 * mult)
		if (s2_mapped < 100):
			s2_mapped = 100
		elif (s2_mapped > 310):
			s2_mapped = 310

		s3_mapped += arm_inputs.read("theta3")
		#if (s3_mapped > 100 or s3_mapped < 310): s3_mapped += ((servo3 + 0.5) * 2 * mult)
		if (s3_mapped < 100):
			s3_mapped = 100
		elif (s3_mapped > 310):
			s3_mapped = 310
	# If endpoint control is disabled use joint control as default
	else:
		servo1 = arm_inputs.read("S1_LEFT") - arm_inputs.read("S1_RIGHT") 
		s1_mapped = round(map(servo1, -1,1, 10, 420), 1)
		
		servo2 = arm_inputs.read("S2_FORWARD") - arm_inputs.read("S2_BACK")
		s2_mapped = round(map(servo2, -1,1, 10, 420), 1)
		
		servo3 = arm_inputs.read("S3_FORWARD") - arm_inputs.read("S3_BACK")
		s3_mapped = round(map(servo3, -1,1, 10, 420), 1)
		
	# Servo 4 is the end effector, independent of joint/endpoint control
	servo4 = arm_inputs.read("S4_OPEN") + arm_inputs.read("S4_CLOSE")
	s4_mapped = round(map(servo4, -1,1, 100, 200), 1)
	
	# Servo 5 is not currently necessary (or even installed) on Nautilus
	servo5 = arm_inputs.read("S5_CW") - arm_inputs.read("S5_CCW") #servo5 currently not on nautilus
	s5_mapped = 0
	
	output = add_next(output, str(round(s1_mapped)))
	output = add_next(output, str(round(s2_mapped)))
	output = add_next(output, str(round(s3_mapped)))
	output = add_next(output, str(round(s4_mapped)))
	output = add_next(output, str(round(s5_mapped)))

	# ------ End Token ------
	output = add_next(output, '*')

	return(output)
	


# function: map()
# description: converts one range of values to a different range of values
def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min	



# function: add_next()
# description: add the next token to the message, seperated by a comma and space
def add_next(base, new):
	return base + ", " + new

