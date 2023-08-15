from packages.camera.CameraSupplier import *
from imports import *
import threading


#Camera global variables
windows = [0,0,0,0,0,0,0,0,0,0]
vss = []
numwindows = 0
newCam = None

lights = True
headinglock = True
depthlock = True
emergency = True


def addWindow():
    global numwindows,windows,vss

    if numwindows < 5:
        numwindows = numwindows + 1
        windows[numwindows-1] = ("frame" + str(numwindows))
    newCam = Cam()
    newCam.start()

def beginVideoThread():
    a = threading.Thread(target=displayVideo, name='Thread-a', daemon=True) #Q: is this used anymore??
    a.start()

def displayVideo():

    video = Video()
    while(True):

        if not video.frame_available():
            continue

        frame = video.frame()
        cv2.imshow('frame', frame)
        #print('abcd')
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def removeWindow():
    global numwindows,windows
    if numwindows > 0:
        cv2.destroyWindow("frame" + str(numwindows))
        numwindows = numwindows - 1
        windows[numwindows] = 0

def toggle_lights():
    global lights
    lights = not lights
    vss[0].updateLights(lights)

def toggle_depth():
    global depthlock
    depthlock = not depthlock
    #update camera
    vss[0].updateDepthLock(depthlock)
    #send update signal

def cam_init():
	#vss.append(Cam().start())
    global newCam
    print("cam trying to start")

    newCam = Cam()
    print("cam trying to start")

    newCam.start()

	#Testing the camera
    # vss[0].updateLights(lights)
    # vss[0].updateEmergencySignal(emergency)
    # vss[0].updateDepthLock(depthlock)
    # vss[0].updateHeadingLock(headinglock)

def cam_update(heading, depth):
    global numwindows
    #vss[0].vssTest()
    newCam.updateLights(lights)
    newCam.updateDepthLock(depthlock)
    newCam.updateEmergencySignal(emergency)
    newCam.updateHeadingLock(headinglock)
    newCam.updateHeading(heading)
    newCam.updateDepth(depth)

    # vss[0].updateLights(lights)
    # vss[0].updateEmergencySignal(emergency)
    # vss[0].updateDepthLock(depthlock)
    # vss[0].updateHeadingLock(headinglock)

    # frame = vss[0].read()
    # for i in range(numwindows):
	#     cv2.namedWindow(windows[i])
	#     cv2.imshow('frame',frame)
#        cv2.imshow(windows[i], frame)
        

def cam_kill():
    vss[0].kill()

