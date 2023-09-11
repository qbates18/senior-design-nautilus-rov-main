# file: control_functions.py
# description: this file defines the commands issued when certain GUI buttons are pressed. Seems to be Obsolete.

import config
import packages.camera.cam as cam
# import cv2

def dummy():
	print("dummy")
#contains control functions that are triggered on each event in the gui
#each function sends the corresponding nmea string to the ros transmission node

def update(event, val_name, value):
	if not config.top_data.assign(val_name, value):
		print("assign failed")

	if val_name == "L_TOG" and value == 1:
		cam.toggle_lights()


def sample():
	print("sample")




# def addWindow():
#	global numwindows,windows,vss
#	print("added window")
#    print(numwindows)
#	if numwindows < 5:
#		numwindows = numwindows + 1
#		windows[numwindows-1] = ("frame" + str(numwindows))

#def removeWindow():
#    global numwindows,windows
#    if numwindows > 0:
#        cv2.destroyWindow("frame" + str(numwindows))
#        numwindows = numwindows - 1
#        windows[numwindows] = 0

# def toggle_lights():
#     global lights
#     lights = not lights
#     vss[0].updateLights(lights)

# def toggle_depth():
#     global depthlock
#     depthlock = not depthlock
#     #update camera
#     vss[0].updateDepthLock(depthlock)
#     #send update signal