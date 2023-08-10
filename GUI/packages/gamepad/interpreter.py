from packages.models.input import Data
import config
import numpy as np
import math
import scipy
from scipy import integrate
import pygame
import os
import time

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


def end_point(xDot = 0.0, yDot = 0.0, zDot = 0.0):
    global thetas, deltaThetas, previousThetaDots, L1, L2, gain

    xDots = np.array([[xDot], [yDot], [zDot]])

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

    thetaDots = np.matmul(inv_jacobian, xDots)

    thetaDots = thetaDots * gain
    #print(thetaDots)


    for x in range(3):        
        deltaThetas[x][0] = gain * (time_step * (thetaDots[x][0] + previousThetaDots[x][0]) * .5)
    #print("\n")
    previousThetaDots = thetaDots
    #integration_thetaDots = np.array([[thetaDots[0][0], thetaDots[1][0], thetaDots[2][0]]])
    #print(deltaThetas)
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


def interpret(gamepad):
	
	#takes a gamepad object
	#return an inputData class corresponding to the controller input 
	
	
	
	for entry in config.top_data.val_names:
		
		x = convert(gamepad.read_value(config.map_dict[entry]))
		#if(entry == "UP"):
		#	print(x)
		config.top_data.assign(entry, x)
		#print all values of top data for debug
		#config.top_data.printclass()
		
# interprets mapping for second controller
def interpret2(gamepad2):
	
	
	for entry in config.arm_inputs.val_names:
		if(entry != "theta1" and entry != "theta2" and entry != "theta3"):
			x = convert(gamepad2.read_value(config.map2_dict[entry]))
			config.arm_inputs.assign(entry, x)

		# ********************************************
		# VALUES MAP TO VALUES FROM 0 - 1
		# ********************************************
		#config.arm_inputs.printclass()
	x_dot = config.arm_inputs.read("S1_LEFT") - config.arm_inputs.read("S1_RIGHT")
	#y_dot = config.arm_inputs.read("S2_FORWARD") - config.arm_inputs.read("S3_BACK")
	theta_radians = end_point(x_dot, 0.0, 0.0)
	theta_degrees = (theta_radians * 180) / math.pi
	theta_degrees = theta_degrees / 1.6

	print(theta_degrees)
	config.arm_inputs.assign("theta1", theta_degrees[0][0])
	config.arm_inputs.assign("theta2", theta_degrees[1][0])
	config.arm_inputs.assign("theta3", theta_degrees[2][0])



def generate_dictionaries(filename):
	#gamepad_dict
	#for each line in map.txt
	#create a dictionary entry: 'VAL_NAME : BUTTON_NAME'
	
	filepath = "packages/gamepad/" + filename
	
	# create gamepad2's dict if gamepad's dict is already created
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
		

	if config.map_dict != None:
		return 

	dictionary = {}

	file = open(filepath, 'r')
	
	for line in file:
		line = line.rstrip('\n')
		split = line.split("=")
		dictionary[split[0].strip()] = split[1].strip()

	#rint(dictionary)
	file.close()

	config.map_dict =  dictionary

def convert(input):
	if input is None:
		return 0
	elif input is True:
		return 1
	elif input is False:
		return 0
	else:
		return input
