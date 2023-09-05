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

def generate(input, subData, closed_loop_dict, pid_dict, arm_disarm_value, arm_inputs):
	global ack_id

	global l_tog_flag
	global s_tog_flag
	global s1_mapped, s2_mapped, s3_mapped, s4_mapped, s5_mapped  
	

	temp_pres = subData.read("PRES")
	temp_tmpr = subData.read("TMPR")
	temp_alt = subData.read("ALT")
	temp_head = subData.read("HEAD")

	#start of string
	output =  "$"

	#ack id
	output = add_next(output, str(ack_id))

	#joystick magnitude and angle calculation
	x = min(input.read("RIGHT") - input.read("LEFT"), 1)
	y = min(input.read("FORWARD") - input.read("BACK"), 1)

	# print("------------")
	# print(x)
	# print(y)

	mag = joystick_mag_calc(x, y)

	#if magnitude is above sensitivity threshold, then calculate angle, otherwise set both values to 0
	if mag >= config.THRESHOLD:
		mag = format(mag, '.3f')
		angle = format(joystick_angle_calc(x, y), '.3f')
	else:
		mag = 0.000
		angle = 0.000

	#for sending down magnitude and angle of left joystick
	#output = add_next(output, str(mag))
	#output = add_next(output, str(angle))

	#for sending down x and y values of left joystick
	output = add_next(output, str(x))
	output = add_next(output, str(y))


	# #vertical magnitude
	#value is changed to be 0 or 1 based on a value which will be changed in the GUI later
	
	
	#if both the depth and altitude closed loop enables are off then calculate verticals normally
	if closed_loop_dict["depth"] == 0 and closed_loop_dict["altitude"] == 0:
		# takes analog value from 0 to 1 for each up and down
		if input.read("UP") > 0 and input.read("DOWN") == 0:
	 		output = add_next(output, str(format(input.read("UP"), '.3f')))
		elif input.read("UP") == 0 and input.read("DOWN") < 0:
	 		output = add_next(output, str(format(input.read("DOWN"), '.3f')))
		else:
			output = add_next(output, str(format(0, '.3f')))
	
	#if altitude lock is enabled
	elif closed_loop_dict["depth"] == 0 and closed_loop_dict["altitude"] == 1:
		#use vert closed loop control
		output = add_next(output, str(format(pid_dict["altitude"].calculate_next(temp_alt), '.3f'))) 
		#print(pid_dict["altitude"].calculate_next(temp_alt))

	#if depth lock is enabled
	elif closed_loop_dict["depth"] == 1 and closed_loop_dict["altitude"] == 0:
		#use vert closed loop control
		output = add_next(output, str(format(pid_dict["depth"].calculate_next(temp_pres), '.3f'))) 
		#print(pid_dict["depth"].calculate_next(temp_pres))
	else:
		output = add_next(output, str(format(0, '.3f')))
	


	# #rotational magnitude
	#takes analog value from 0 to 1 for either rotation side

	#if 0 closed loop off, if 1 then closed loop on, otherwise default to off
	if closed_loop_dict["head"] == 0:
		if input.read("ROT_CW") > config.THRESHOLD and input.read("ROT_CCW") == 0:
	 		output = add_next(output, str(format(input.read("ROT_CW"), '.3f')))
		elif input.read("ROT_CW") == 0 and input.read("ROT_CCW") > config.THRESHOLD:
	 		output = add_next(output, str(format(-input.read("ROT_CCW"), '.3f')))
		else:
			output = add_next(output, str(format(0, '.3f')))
	elif closed_loop_dict["head"] == 1:
		#use heading closed loop control
		output = add_next(output, str(format(pid_dict["head"].calculate_next(temp_head), '.3f')))
		#print(pid_dict["head"].calculate_next(temp_head))
	else:
		output = add_next(output, str(format(0, '.3f')))


	# if input.read("ROT_CW") == 1 and input.read("ROT_CCW") == 0:
	#  	output = add_next(output, str(format(1, '.3f')))
	# elif input.read("ROT_CW") == 0 and input.read("ROT_CCW") == 1:
	#  	output = add_next(output, str(format(-1, '.3f')))
	# else:
	# 	output = add_next(output, str(format(0, '.3f')))


	#light toggle
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

	# #sampler toggle
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

	# #camera tilt
	if input.read("CAM_UP") == 1 and input.read("CAM_DN") == 0:
		output = add_next(output, 'U')
	elif input.read("CAM_UP") == 0 and input.read("CAM_DN") == 1:
		output = add_next(output, 'D')
	else:
		output = add_next(output, 'S')

	#arm/disarm value
	output = add_next(output, str(arm_disarm_value))
	


	# robot arm servo values
	# reads controller values and maps them to pwm values for servos
	# robot arm servo controller pins 0,2,12,14,15 from left to right servo1-servo5
	
	mult = 30 # movement multiplier, increase mult to increase servo speed

	if(endpoint_control_flag):
		#print(arm_inputs.read("theta1"))
		#print(arm_inputs.read("theta2"))
		#print(arm_inputs.read("theta3"))

		s1_mapped += arm_inputs.read("theta1")
		if (s1_mapped < 100):
			s1_mapped = 100
		elif (s1_mapped > 310):
			s1_mapped = 310

		servo2 = 0 #Q: why is this set to 0 and not reading theta2
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
	else:

		servo1 = arm_inputs.read("S1_LEFT") - arm_inputs.read("S1_RIGHT") 
		#s1_mapped += (servo1 * mult)
		s1_mapped = round(map(servo1, -1,1, 60, 90), 1)
		
		servo2 = arm_inputs.read("S2_FORWARD") - arm_inputs.read("S2_BACK")
		s2_mapped = round(map(servo2, -1,1, 10, 420), 1)
		
		servo3 = arm_inputs.read("S3_FORWARD") - arm_inputs.read("S3_BACK")
		s3_mapped = round(map(servo3, -1,1, 10, 420), 1)
		
	
	servo4 = arm_inputs.read("S4_OPEN") + arm_inputs.read("S4_CLOSE")
	s4_mapped = round(map(servo4, -1,1, 100, 200), 1)
	#if (s4_mapped > 100 or s4_mapped < 270): 
	#	s4_mapped += (servo4 * mult)
	#if (s4_mapped < 100):
	#	s4_mapped = 100
	#elif (s4_mapped > 270):
	#	s4_mapped = 270
	
	servo5 = arm_inputs.read("S5_CW") - arm_inputs.read("S5_CCW") #servo5 currently not on nautilus
	s5_mapped = 0
	#s5_mapped += (servo5 * mult)
	#if (s5_mapped < 10):
	#	s5_mapped = 10
	#elif (s5_mapped > 420
	#	s5_mapped = 420
	
	#s5_mapped = round(map(servo5, -1,1, 0, 0), 1)
	
	output = add_next(output, str(round(s1_mapped)))
	output = add_next(output, str(round(s2_mapped)))
	output = add_next(output, str(round(s3_mapped)))
	output = add_next(output, str(round(s4_mapped)))
	output = add_next(output, str(round(s5_mapped)))

	#end of string
	output = add_next(output, '*')

	#print(output)
	ack_id = ack_id + 1

	return(output)
	
	
def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min	

def add_next(base, new):
	return base + ", " + new

def joystick_angle_calc(x, y):
        #QUADRANT II
        if x < 0 and y >= 0:
            return round(math.degrees(math.atan(y/x)), 3) + 180

        #QUADRANT III
        elif x < 0 and y <= 0:
            return round(math.degrees(math.atan(y/x)), 3) - 180

        #BETWEEN II AND III AND III AND IV
        #since x can equal 0, need to have case so not dividing by 0
        elif x == 0:
            if y > 0:
                return 90
            else:
                return -90
       
        #QUADRANT I
        #QUADRANT IV
        else: 
            return round(math.degrees(math.atan(y/x)), 3) 
       
def joystick_mag_calc(x, y):
    return min(round((x**2 + y**2)**0.5, 3), 1)


if __name__ == '__main__':

	while True:
		test = inputClass(0.5, 0.6, 0.1, 0.23, 1, 0, 1)
		generate(test)
		time.sleep(0.5)
