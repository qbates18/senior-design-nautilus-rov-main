# file: controls.py
# description: old control method, where printing commands worked with ROS nodes to send the data to the ROV

#Q: Isnt this obsolete? ROS was removed by the 2020-2021 team...

#contains control functions that are triggered on each event in the gui or by 
#each function sends the corresponding nmea string to the ros transmission node


def forward():
	print("forward")

def backward():
	print("backward")

def left():
	print("left")

def right():
	print("right")

def rotate_cw():
	print("cw")

def rotate_ccw():
	print("ccw")

def up():
	print("up")

def down():
	print("down")

def toggle_lights():
	print("light")

def camtilt_up():
	print("cam up")

def camtilt_down():
	print("cam down")

def sample():
	print("sample")