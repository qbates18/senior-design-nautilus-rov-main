
import numpy as np
import math
import time
from packages.gamepad.ps4 import PS4Controller as Gamepad
import pygame

# Variables for endpoint control
thetas = np.array([[math.pi/4], [0.0], [math.pi/4]])
previousThetaDots = np.array([[0.0], [0.0], [0.0]])
deltaThetas = np.array([[0.0], [0.0], [0.0]])
L1 = 17
L2 = 11
firstRunFlag=False
startTime=time.time()

def end_point(xDot = 0.0, yDot = 0.0, zDot = 0.0):
    global thetas, deltaThetas, previousThetaDots, L1, L2, firstRunFlag, startTime

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

	# ------ Calculate the change in theta ------
    deltaTime=time.time()-startTime
    for x in range(3):        
        deltaThetas[x][0] = deltaTime * (thetaDots[x][0] + previousThetaDots[x][0]) * .5
    previousThetaDots = thetaDots
    startTime=time.time()

	# ------ Calculate the XYZ coordinates of the end effector ------
    thetas = thetas + deltaThetas
    #print((thetas * 180) / math.pi)
    t1 = thetas[0][0]
    t2 = thetas[1][0]
    t3 = -thetas[1][0]
    t4 = thetas[2][0]
    x = (L1 / 2) * math.cos(t1 + t2) + (L1 / 2) * math.cos(t1 - t2) + L2 * math.cos(t1 + t4)
    y = (L1 / 2) * math.sin(t1 + t2) + (L1 / 2) * math.sin(t1 - t2) + L2 * math.sin(t1 + t4)
    z = -L1 * math.sin(t2) - L2 * math.sin(t2 + t3) * math.cos(t4)
    print("X: {}".format(x))
    print("Y: {}".format(y))
    print("Z: {}\n".format(z))

    return thetas

if __name__ == "__main__":
    controllerFlag=True
    if(controllerFlag):
        pygame.init()
        gamepad = Gamepad()
        gamepad2= Gamepad()
    else:
        xdot=0
        ydot=1
        zdot=0
    
    while(True):
        if(controllerFlag):
            gamepad.listen(gamepad2)
            xdot=gamepad.read_value("JOY1_LT")-gamepad.read_value("JOY1_RT")
            ydot=0.0
            #ydot=gamepad.read_value("JOY1_UP")-gamepad.read_value("JOY1_DN")
            zdot=0.0
            #zdot=gamepad.read_value("JOY2_UP")-gamepad.read_value("JOY2_DN")
            print("Xc: {}".format(xdot))
            print("Yc: {}".format(ydot))
            print("Zc: {}\n".format(zdot))
        theta_radians = end_point(xdot, ydot, zdot)
        theta_degrees = (theta_radians * 180) / math.pi
        theta_degrees = theta_degrees * 10 / 3 #3.3333 is the gear ratio
        
        print("Theta1: {}".format(theta_degrees[0][0]))
        print("Theta2: {}".format(theta_degrees[1][0]))
        print("Theta3: {}\n".format(theta_degrees[2][0]))

        time.sleep(1)