#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file presents an interface for interacting with the Playstation 4 Controller
# in Python. Simply plug your PS4 controller into your computer using USB and run this
# script!
#
# NOTE: I assume in this script that the only joystick plugged in is the PS4 controller.
#       if this is not the case, you will need to change the class accordingly.
#
# Copyright © 2015 Clay L. McLeod <clay.l.mcleod@gmail.com>
#
# Distributed under terms of the MIT license.

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" #stops pygame message from printing to console on startup
import pygame
import time
import math 



class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    button_data = None
    hat_data = None
    axis_data = None

    def init(self, num):
        """Initialize the joystick components"""
        
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            return False
            

        self.controller = pygame.joystick.Joystick(num)
        self.controller.init()

        print(self.controller.get_name())
	
        if not self.axis_data:
            self.axis_data = {}
            for i in range(self.controller.get_numaxes()):
                self.axis_data[i] = 0

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        return True

    def listen(self, gamepad2):
        """Listen for events to happen"""   
        for event in pygame.event.get():
            
            #Gamepad 1
            if ("{'joy': 0" in str(event)):
               #BUTTON PRESS
               if event.type == pygame.JOYBUTTONDOWN:
                   self.button_data[event.button] = True

               #BUTTON RELEASE
               elif event.type == pygame.JOYBUTTONUP:
                   self.button_data[event.button] = False

               #DIRECTIONAL PAD
               elif event.type == pygame.JOYHATMOTION:
                   if event.hat == 0:
                       self.hat_data = event.value
		    
               #JOYSTICKS
               if event.type == pygame.JOYAXISMOTION:
                   if event.axis == 4 or event.axis == 5:
                       self.axis_data[event.axis] = round(event.value, 3)/2 + 0.5
                   else:
                       self.axis_data[event.axis] = round(event.value, 3)
            #Gamepad 2
            else:
                #BUTTON PRESS
                if event.type == pygame.JOYBUTTONDOWN:
                    gamepad2.button_data[event.button] = True

                #BUTTON RELEASE
                elif event.type == pygame.JOYBUTTONUP:
                    gamepad2.button_data[event.button] = False

                #DIRECTIONAL PAD
                elif event.type == pygame.JOYHATMOTION:
                    if event.hat == 0:
                        gamepad2.hat_data = event.value
		    
                #JOYSTICKS
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 4 or event.axis == 5:
                        gamepad2.axis_data[event.axis] = round(event.value, 3)/2 + 0.5
                    else:
                        gamepad2.axis_data[event.axis] = round(event.value, 3)

            

    def check(self):
        pygame.joystick.quit()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
        if not joystick_count: 
            if not discon:
                print("reconnect you meat bag")
                discon = True
            clock.tick(20)
            check_pad()
        else:
            discon = False

    button_id = {
    0 : "X",
    1 : "CIRCLE",
    2 : "TRIANGLE",
    3 : "SQUARE",
    4 : "L1",
    5 : "R1",
    6 : "L2",
    7 : "R2",
    8 : "SHARE",
    9 : "OPTIONS",
    10 : "PS",
    11 : "LCLICK",
    12 : "RCLICK",
    13 : "TOUCHPAD"
}

    def read_value(self, button):
        if button == "X":
            return self.button_data[0]
        elif button == "CIRCLE":
            return self.button_data[1]
        elif button == "TRIANGLE":
            return self.button_data[2]
        elif button == "SQUARE":
            return self.button_data[3]
        elif button == "L1":
            return self.button_data[4]
        elif button == "R1":
            return self.button_data[5]
        elif button == "L2_PRESS":
            return self.button_data[6]
        elif button == "R2_PRESS":
            return self.button_data[7]
        elif button == "SHARE":
            return self.button_data[8]
        elif button == "OPTIONS":
            return self.button_data[9]
        elif button == "PS":
            return self.button_data[10]
        elif button == "LCLICK":
            return self.button_data[11] 
        elif button == "RCLICK":
            return self.button_data[12] 
        elif button == "TOUCHPAD":
            return self.button_data[13]
        elif button == "DPAD_U":
            if self.hat_data == (0, 1):
                return True
            else:
                return False 
        elif button == "DPAD_R":
            if self.hat_data == (1, 0):
                return True
            else:
                return False
        elif button == "DPAD_D":
            if self.hat_data == (0, -1):
                return True
            else:
                return False
        elif button == "DPAD_L":
            if self.hat_data == (-1, 0):
                return True
            else:
                return False

        elif button == "JOY1_UP":
            #print(self.axis_data[1])
            return -min(self.axis_data[1], 0)
        elif button == "JOY1_RT":
            return max(self.axis_data[0], 0)
        elif button == "JOY1_DN":
            return max(self.axis_data[1], 0)
        elif button == "JOY1_LT":
            return -min(self.axis_data[0], 0)

        elif button == "JOY2_UP":
            return -min(self.axis_data[4], 0)
        elif button == "JOY2_RT":
            return max(self.axis_data[3], 0)
        elif button == "JOY2_DN":
            return max(self.axis_data[4], 0)
        elif button == "JOY2_LT":
            return -min(self.axis_data[3], 0)

        elif button == "JOY2X":
            return self.axis_data[2]
        elif button == "JOY2Y":
            return self.axis_data[3]
        elif button == "L2_ANLG":
            return -max(self.axis_data[2], 0)
        elif button == "R2_ANLG":
            return self.axis_data[5]
        
        


#2 L2_ANLG
#3 JOY2_LTRT
#4 JOY2_UPDN
#5 R2_ANLG


                        
                    
if __name__ == '__main__':

    ps4 = PS4Controller()
    ps4.init()


    while True:
        ps4.listen()

        #print(ps4.axis_data[1])
        print(ps4.axis_data[5])
        #print(ps4.button_data[13])
        #if ps4.hat_data == (-1, 0):
            #print(True)
        #else:
            #print(False)
        #time.sleep(1)

                       



