# file: interpreter.py
# description: interprets controller inputs into commands to actuate different parts of the ROV

from packages.models.input import Data
import config
import numpy as np
import math
import scipy
from scipy import integrate
import pygame
import os
import time

# Variables for endpoint control
angle1Old = 30.0
angle2Old = 30.0
angle3Old = 30.0
angle1New = None
angle2New = None 
angle3New = None
thetas = np.array([[math.pi/4], [0.0], [math.pi/4]])
previousThetaDots = np.array([[0.0], [0.0], [0.0]])
deltaThetas = np.array([[0.0], [0.0], [0.0]])
L1 = 17
L2 = 11
gain = 10
time_step = .001



# function: end_point():
# description: calculates joint values to move end effector in XYZ as commanded by controller inputs
# input: 
def end_point(xDot = 0.0, yDot = 0.0, zDot = 0.0):
    global thetas, deltaThetas, previousThetaDots, L1, L2, gain

    xDots = np.array([[xDot], [yDot], [zDot]])

	# ------ Create inverse jacobian matrix ------
    t1 = thetas[0][0]
    t2 = thetas[1][0]
    t3 = -thetas[1][0]
    t4 = thetas[2][0]
    a = -(L1 * math.sin(t1 + t2)) / 2 - (L1 * math.sin(t1 - t2)) / 2 - L2 * math.sin(t1 + t4)
    b = (-L1 * math.sin(t1 + t2)) / 2 + (L1 * math.sin(t1 - t2)) / 2
    c = -L2 * math.sin(t1 + t4)
    d = (L1 * math.cos(t1 + t2)) / 2 + (L1 * math.cos(t1 - t2)) / 2 + L2 * math.cos(t1 + t4)
    e = (L1 * math.cos(t1 + t2)) / 2 - (L1 * math.cos(t1 - t2)) / 2
    f = L2 * math.cos(t1 + t4)
    g = -L1 * math.cos(t2) - L2 * math.cos(t2 + t3) * math.cos(t4)
    jacobian = np.array([[a, b, c], [d, e, f], [0, g, 0]])
    inv_jacobian = np.linalg.inv(jacobian)

	# ------ Calculate the theta dots ------
    thetaDots = np.matmul(inv_jacobian, xDots)
    thetaDots = thetaDots * gain

	# ------ Calculate the change in theta ------
    for x in range(3):        
        deltaThetas[x][0] = gain * (time_step * (thetaDots[x][0] + previousThetaDots[x][0]) * .5)
    previousThetaDots = thetaDots

	# ------ Calculate the XYZ coordinates of the end effector ------
    thetas = thetas + deltaThetas
    print((thetas * 180) / math.pi)
    t1 = thetas[0][0]
    t2 = thetas[1][0]
    t3 = -thetas[1][0]
    t4 = thetas[2][0]
    x = (L1 / 2) * math.cos(t1 + t2) + (L1 / 2) * math.cos(t1 - t2) + L2 * math.cos(t1 + t4)
    y = (L1 / 2) * math.sin(t1 + t2) + (L1 / 2) * math.sin(t1 - t2) + L2 * math.sin(t1 + t4)
    z = -L1 * math.sin(t2) - L2 * math.sin(t2 + t3) * math.cos(t4)
    print("X: {}\n".format(x))
    print("Y: {}\n".format(y))
    print("Z: {}\n".format(z))

    return deltaThetas



# function: interpret()
# description: takes input from a controller and maps it to top_data, the values sent to the ROV to control motion
# input: a gamepad object
def interpret(gamepad):
	for entry in config.top_data.val_names:
		x = convert(gamepad.read_value(config.map_dict[entry]))
		config.top_data.assign(entry, x)
		#print all values of top data for debug
		#config.top_data.printclass()
		


# fucntion: interpret2()
# description: takes input from a controller and mapts to arm_inputs, the values sent to the ROV to control arm manipulation. Both joint and endpoint control values are calculated.	
# input: a gamepad object	
def interpret2(gamepad2):
	# ------ Assign joint control values ------
	for entry in config.arm_inputs.val_names:
		if(entry != "theta1" and entry != "theta2" and entry != "theta3"):
			x = convert(gamepad2.read_value(config.map2_dict[entry]))
			config.arm_inputs.assign(entry, x)

	# ------ Calculate and assign endpoint values ------
	x_dot = config.arm_inputs.read("S1_LEFT") - config.arm_inputs.read("S1_RIGHT")
	#y_dot = config.arm_inputs.read("S2_FORWARD") - config.arm_inputs.read("S3_BACK") # CURRENTLY YDOT (VERTICAL) ENPOINT CONTROL HAS NOT BEEN FINISHED
	theta_radians = end_point(x_dot, 0.0, 0.0)
	theta_degrees = (theta_radians * 180) / math.pi
	theta_degrees = theta_degrees / 1.6 #1.6 is the gear ratio
	config.arm_inputs.assign("theta1", theta_degrees[0][0])
	config.arm_inputs.assign("theta2", theta_degrees[1][0])
	config.arm_inputs.assign("theta3", theta_degrees[2][0])



# function: generate_dictionaries()
# description: create a dictionary to assign controller inputs to desired variables. This should run for each controller being used.
# input: text file
def generate_dictionaries(filename):

	#for each line in map.txt (the input text file)
	#create a dictionary entry: 'VAL_NAME : BUTTON_NAME'
	
	filepath = "packages/gamepad/" + filename
	
	# ------ Create gamepad2's dict if gamepad's dict is already created ------
	# we only want to generate gamepad2's dict if gamepad's dict is already created
	if config.gamepad2_flag and config.map_dict != None:
		if config.map2_dict != None:
			return
		dictionary2 = {}
		file = open(filepath, 'r')
		for line in file:
			line = line.rstrip('\n')
			split = line.split("=")
			dictionary2[split[0].strip()] = split[1].strip()
		file.close()
		config.map2_dict = dictionary2
		return

	# ------ Check if the first gamepad dict has been created ------
	if config.map_dict != None:
		return 

	# ------ Create the first gamepad dict -------
	dictionary = {}
	file = open(filepath, 'r')
	for line in file:
		line = line.rstrip('\n')
		split = line.split("=")
		dictionary[split[0].strip()] = split[1].strip()
	file.close()
	config.map_dict =  dictionary



# function: convert()
# description: convert input data into numerical values
# input: gamepad input 
def convert(input):
	if input is None:
		return 0
	elif input is True:
		return 1
	elif input is False:
		return 0
	else:
		return input
