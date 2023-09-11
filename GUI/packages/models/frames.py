# file: frames.py
# description: creates the structure of the GUI

import tkinter as tk                # python 3
from packages.closed_loop.RotationCounter import *
from packages.closed_loop.PIDs import *

from packages.models.control_functions import *
from packages.camera.cam import *
import packages.models.graphs as graphs


class neptuneGUI(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		self.minsize(1080, 720)
		self.main_widgets()

	
	def main_widgets(self):
		self.tmen = topMenu(self)

		self.stat = statusFrame(self)
		self.stat.pack(side = "bottom", fill = "both")

		self.sens = sensorFrame(self)
		self.sens.pack(side = "right", fill = "both", expand = True)

		self.control = controlFrame(self)
		self.control.pack(side = "right", fill = "y")


	def status_display(self, data):
		self.stat.display(data)

	def sensor_display(self, field, data):
		self.sens.display(field, data)

	def sensor_animate(self, rate):
		return self.sens.animate(rate)
		
	def rotation_display(self, data):
		#print(data)
		self.control.man.rotationCounter(data)

	def sensor_readout(self, tmpr, depth, head, altitude, voltage):
		self.control.man.update_SensorReadout(tmpr, depth, head, altitude, voltage)
	
	def closed_loop_control(self):
		return self.control.man.return_closed_loop_control()

	def return_pids(self):
		return self.control.man.return_closed_loop_pids()
	
	def return_arm(self):
		return self.control.arm.return_arm_value()

class neptuneLayout(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent, bg = "red")
	
class topMenu:
	def __init__(self, parent):
		menu_top = tk.Menu(parent)
		parent.config(menu=menu_top)

		sub_help = tk.Menu(menu_top)
		menu_top.add_cascade(label="Help", menu=sub_help)
		sub_help.add_command(label="Controls", command=dummy)
		sub_help.add_command(label="About Neptune", command=dummy)

		sub_windows = tk.Menu(menu_top)
		menu_top.add_cascade(label="Windows", menu=sub_windows)
		sub_windows.add_command(label="Add Camera Feed", command=addWindow)
		#sub_windows.add_command(label="Add Camera Feed", command=lambda: beginThreading()) #Q: I think this is depreicated
		sub_windows.add_command(label="Remove Camera Feed", command=removeWindow)


class squareButton(tk.Frame):
	def __init__(self, parent, width, height, text, command = None, padx = 0, pady = 0):
		tk.Frame.__init__(self, parent, width = width, height = height, bg = parent.bg)
		self.grid_propagate(False) 
		self.columnconfigure(0, weight=1) 
		self.rowconfigure(0,weight=1) 

		self.button = tk.Button(self, text = text, command = command)
		
		self.button.grid(sticky="wens", padx = padx, pady = pady) 
	
	def bind(self, event, handler):
		self.button.bind(event, handler)


class squareEmpty(tk.Frame):
	def __init__(self, parent, width, height):
		tk.Frame.__init__(self, parent, width = width, height = height, bg = parent.bg)
		self.grid_propagate(False) 
		self.columnconfigure(0, weight=1) 
		self.rowconfigure(0,weight=1)



class controlFrame(tk.Frame):

	def __init__(self, parent):
		self.width = 300
		self.parent = parent
		self.bg = "azure2"

		tk.Frame.__init__(self, parent, width = self.width, bg = self.bg, bd = 1)
		self.pack_propagate(False)

		self.widgets()
	
	def widgets(self):
		self.man = movementControl(self)
		self.man.pack(side = "bottom", fill = "x")

		self.arm = armFrame(self)
		self.arm.pack(side = "bottom", fill = "x")

#		self.ltog = lightControl(self)
#		self.ltog.pack(side = "left", anchor = "sw")

#		self.stog = samplerControl(self)
#		self.stog.pack(side = "left", anchor = "sw")

#		self.cam = camControl(self)
#		self.cam.pack(side = "left", anchor = "sw")

class armFrame(tk.Frame):
	def __init__(self, parent):
		self.parent = parent

		self.bg = "gray70"
		self.highlightbackground = "gray10"
		self.highlightthickness = 1
		self.relief = "raised"

		tk.Frame.__init__(self, parent, height=400, bg = self.bg, bd = 1, highlightbackground = self.highlightbackground, highlightthickness = self.highlightthickness, relief = self.relief)
		self.grid_propagate(False)

		self.arm_value = 0

		self.widgets()
	
	def widgets(self):

		self.armButton = Button(self, text="ROV DISARMED", command=self.arm_ROV, bg="green", fg="white")
		self.armButton.grid(row=0, column=0, columnspan=6)
		# self.ltog = lightControl(self)
		# self.ltog.grid(row=0, column=0, columnspan=6)

		# self.stog = samplerControl(self)
		# self.stog.grid(row=0, column=7, columnspan=6)

		# self.cam = camControl(self)
		# self.cam.grid(row=2, column=0, columnspan=6)
	
	def arm_ROV(self):
		if self.armButton['text'] == "ROV DISARMED":
			self.armButton['text'] = "ROV ARMED"
			self.armButton['bg'] = "red"
			self.arm_value = 1
		
		elif self.armButton['text'] == "ROV ARMED":
			self.armButton['text'] = "ROV DISARMED"
			self.armButton['bg'] = "green"
			self.arm_value = 0

		else:
			self.armButton['text'] = "ROV DISARMED"
			self.armButton['bg'] = "green"
			self.arm_value = 0
	
	def return_arm_value(self):
		return self.arm_value

		
class movementControl(tk.Frame):
	def __init__(self, parent):
		self.parent = parent

		self.bg = "gray70"
		self.highlightbackground = "gray10"
		self.highlightthickness = 1
		self.relief = "raised"

		self.rotationValue = 0
		self.tmpr = 0
		self.depth = 0
		self.head = 0
		self.voltage = 0
		self.headlock = 0
		self.altitude = 0

		self.depthLockValue = 0
		self.headingLockValue = 0
		self.altitudeLockValue = 0

		self.closedLoopReturnDict = {"head" : 0, "depth" : 0, "altitude" : 0}
		self.closedLoopPidReturnDict = {"head": None, "depth": None, "altitude": None}

		self.rotationCounter = rotationCounter()

		tk.Frame.__init__(self, parent, height = 200, bg = self.bg, bd = 1, highlightbackground = self.highlightbackground, highlightthickness = self.highlightthickness, relief = self.relief)
		self.grid_propagate(False)
		self.widgets()

	def widgets(self):
		self.lbl = tk.Label(self, text = "Sensor Read Outs", bg = self.bg)
		self.lbl.grid(row = 0, column = 1, columnspan = 7)

		var4 = "HEAD: " + str(self.head)
		self.headLbl = tk.Label(self, text = str(var4))
		self.headLbl.grid(row = 2, column = 0, columnspan = 6)

		var1 = "ROT: " + str(self.rotationValue)
		self.rotLbl = tk.Label(self, text = str(var1))
		self.rotLbl.grid(row = 2, column = 7, columnspan = 6)

		var2 = "TEMP: " + str(self.tmpr) + "C"
		self.tmprLbl = tk.Label(self, text = str(var2))
		self.tmprLbl.grid(row = 3, column = 0, columnspan = 6)

		var3 = "DEPTH: " + str(self.depth) + "m"
		self.depthLbl = tk.Label(self, text = str(var3))
		self.depthLbl.grid(row = 3, column = 7, columnspan = 6)

		var5 = "VOLTAGE: " + str(self.voltage) + "V"
		self.voltageLbl = tk.Label(self, text = str(var5))
		self.voltageLbl.grid(row = 4, column = 0, columnspan = 6)

		var6 = "ALT: " + str(self.altitude) + "m"
		self.altitudeLbl = tk.Label(self, text = str(var6))
		self.altitudeLbl.grid(row = 5, column = 0, columnspan = 6)

		self.headLockButton = Button(self, text="Heading Lock OFF", command=self.enable_head_lock, bg="red", fg="white")
		self.headLockButton.grid(row=8, column= 4, columnspan = 7)

		self.depthLockButton = Button(self, text="Depth Lock OFF", command=self.enable_depth_lock, bg="red", fg="white")
		self.depthLockButton.grid(row=9, column= 0, columnspan = 5)

		self.altitudeLockButton = Button(self, text="Altitude Lock OFF", command=self.enable_altitude_lock, bg="red", fg="white")
		self.altitudeLockButton.grid(row=9, column= 6, columnspan = 5)

	def update_SensorReadout(self, tmpr, depth, head, altitude, voltage):
		self.rotationValue = self.rotationCounter.calculate_rotation(head)
		self.rotLbl['text'] = "ROT: " + str(format(self.rotationValue, '.2f'))
		
		self.tmpr = tmpr
		self.tmprLbl['text'] = "TEMP: " + str(tmpr) + "C"

		self.depth = depth
		self.depthLbl['text'] = "DEPTH: " + str(depth) + "m"
		
		self.head = head
		self.headLbl['text'] = "HEAD: " + str(head)
		
		self.voltage = voltage
		self.voltageLbl['text'] = "Voltage: " + str(voltage) + "V"

		self.altitude = altitude
		self.altitudeLbl['text'] = "ALT: " + str(altitude) + "m"

		#print(self.rotationValue)
	
	def enable_head_lock(self):
		if self.headLockButton['text'] == "Heading Lock OFF":
			self.headLockButton['text'] = "Heading Lock ON"
			self.headLockButton['bg'] = "green"
			self.closedLoopReturnDict["head"] = 1
			self.closedLoopPidReturnDict["head"] = head_PID(self.head)

		else:
			self.headLockButton['text'] = "Heading Lock OFF"
			self.headLockButton['bg'] = "red"
			self.closedLoopReturnDict["head"] = 0
			self.closedLoopPidReturnDict["head"] = None

	def enable_depth_lock(self):
		if self.depthLockButton['text'] == "Depth Lock OFF":
			self.depthLockButton['text'] = "Depth Lock ON"
			self.depthLockButton['bg'] = "green"
			self.altitudeLockButton['text'] = "Altitude Lock OFF"
			self.altitudeLockButton['bg'] = "red"
			self.closedLoopReturnDict["depth"] = 1
			self.closedLoopReturnDict["altitude"] = 0
			self.closedLoopPidReturnDict["depth"] = depth_PID(self.depth) #Q: keeps yelling at me when i click depth lock that the movementControl object doesnt have the attribite 'pres'

		else:
			self.depthLockButton['text'] = "Depth Lock OFF"
			self.depthLockButton['bg'] = "red"
			self.altitudeLockButton['text'] = "Altitude Lock OFF"
			self.altitudeLockButton['bg'] = "red"
			self.closedLoopReturnDict["depth"] = 0
			self.closedLoopReturnDict["altitude"] = 0

			#replaces the old instance of the PID with nothing, to delete it.
			#that way it can be replaced with a new one with a new desired value
			self.closedLoopPidReturnDict["depth"] = None

		
	def enable_altitude_lock(self):
		if self.altitudeLockButton['text'] == "Altitude Lock OFF":
			self.altitudeLockButton['text'] = "Altitude Lock ON"
			self.altitudeLockButton['bg'] = "green"	
			self.depthLockButton['text'] = "Depth Lock OFF"
			self.depthLockButton['bg'] = "red"
			self.closedLoopReturnDict["depth"] = 0
			self.closedLoopReturnDict["altitude"] = 1
			self.closedLoopPidReturnDict["altitude"] = altitude_PID(self.altitude)

		else:
			self.altitudeLockButton['text'] = "Altitude Lock OFF"
			self.altitudeLockButton['bg'] = "red"
			self.depthLockButton['text'] = "Depth Lock OFF"
			self.depthLockButton['bg'] = "red"
			self.closedLoopReturnDict["depth"] = 0
			self.closedLoopReturnDict["altitude"] = 0

	def return_closed_loop_control(self):
		return self.closedLoopReturnDict
	
	def return_closed_loop_pids(self):
		return self.closedLoopPidReturnDict


class lightControl(tk.Frame):
	def __init__(self, parent):
		self.parent = parent

		self.bg = "gray70"
		self.highlightbackground = "gray30"
		self.highlightthickness = 1
		self.relief = "raised"
			
		self.width = 100
		self.height = 300

		tk.Frame.__init__(self, parent, width = self.width, height = self.height, bg = self.bg, bd = 1, highlightbackground = self.highlightbackground, highlightthickness = self.highlightthickness, relief = self.relief)
		self.pack_propagate(False)
		self.widgets()

	def widgets(self):
		self.ltog_btn = tk.Button(self, text = "Toggle Lights")
		self.ltog_btn.bind("<ButtonPress-1>", lambda event: update(event, val_name = "L_TOG", value = 1))
		self.ltog_btn.bind("<ButtonRelease-1>", lambda event: update(event, val_name = "L_TOG", value = 1))
		self.ltog_btn.pack()


class samplerControl(tk.Frame): #Q: this is no longer a used thing why is it still here
	def __init__(self, parent):
		self.parent = parent

		self.bg = "gray70"
		self.highlightbackground = "gray30"
		self.highlightthickness = 1
		self.relief = "raised"
			
		self.width = 100
		self.height = 300

		tk.Frame.__init__(self, parent, width = self.width, height = self.height, bg = self.bg, bd = 1, highlightbackground = self.highlightbackground, highlightthickness = self.highlightthickness, relief = self.relief)
		self.pack_propagate(False)
		self.widgets()

	def widgets(self):
		self.ltog_btn = tk.Button(self, text = "Toggle Sampler")
		self.ltog_btn.bind("<ButtonPress-1>", lambda event: update(event, val_name = "S_TOG", value = 1))
		self.ltog_btn.bind("<ButtonRelease-1>", lambda event: update(event, val_name = "S_TOG", value = 0))
		self.ltog_btn.pack()


class camControl(tk.Frame):
	def __init__(self, parent):
		self.parent = parent

		self.bg = "gray70"
		self.highlightbackground = "gray30"
		self.highlightthickness = 1
		self.relief = "raised"
			
		self.width = 100
		self.height = 300

		self.buttonsize_x = 48
		self.buttonsize_y = 48
		self.buttonpad_x = 3
		self.buttonpad_y = 3

		tk.Frame.__init__(self, parent, width = self.width, height = self.height, bg = self.bg, bd = 1, highlightbackground = self.highlightbackground, highlightthickness = self.highlightthickness, relief = self.relief)
		self.pack_propagate(False)
		self.widgets()

	def widgets(self):
		self.lbl = tk.Label(self, text = "Camera Control", bg = self.bg)
		self.lbl.pack(pady = 15)

		self.cup_btn = squareButton(self, self.buttonsize_x, self.buttonsize_y, "\u25b2", padx = self.buttonpad_x, pady = self.buttonpad_y)
		self.cup_btn.bind("<ButtonPress-1>", lambda event: update(event, val_name = "CAM_UP", value = 1))
		self.cup_btn.bind("<ButtonRelease-1>", lambda event: update(event, val_name = "CAM_UP", value = 0))
		self.cup_btn.pack()

		self.cdn_btn = squareButton(self, self.buttonsize_x, self.buttonsize_y, "\u25bc", padx = self.buttonpad_x, pady = self.buttonpad_y)
		self.cdn_btn.bind("<ButtonPress-1>", lambda event: update(event, val_name = "CAM_DN", value = 1))
		self.cdn_btn.bind("<ButtonRelease-1>", lambda event: update(event, val_name = "CAM_DN", value = 0))
		self.cdn_btn.pack()

		
class sensorFrame(tk.Frame):
	
	def __init__(self, parent):
		self.parent = parent

		self.bg = "azure3"
		self.highlightbackground = "gray30"
		self.highlightthickness = 1
		self.relief = "raised"
			
		self.width = 800
		self.height = 300


		tk.Frame.__init__(self, parent, width = self.width, height = self.height, bg = self.bg, bd = 1, highlightbackground = self.highlightbackground, highlightthickness = self.highlightthickness, relief = self.relief)
		self.pack_propagate(False)
		self.widgets()



	def widgets(self):
		self.cnvs = canvasFrame(self, graphs.figure)
		self.cnvs.pack(side = "top", fill = "both", expand = True)



	def display(self, field, data):
		
		if field == "ALT":
			graphs.update_data(field, data)

		elif field == "DEPTH":
			graphs.update_data(field, data)

		elif field == "HEAD":
			graphs.update_data(field, data)
			



	def animate(self, rate):
		return graphs.animate(rate)



class canvasFrame(tk.Frame):
	def __init__(self, parent, figure):
		tk.Frame.__init__(self, parent)
	
		self.cvs = graphs.figure_canvas(figure, self)
		self.cvs.draw()
		self.cvs.get_tk_widget().pack(fill="both", expand=True)



class statusFrame(tk.Frame):

	def __init__(self, parent):	
		self.parent = parent
		self.bg = "dim gray"
		self.height = 40

		tk.Frame.__init__(self, self.parent, bg = self.bg, height = self.height)

		self.widgets()

	def widgets(self):
		self.status_label = tk.Label(self, text = "status frame", bg = self.bg)
		self.status_label.pack(side = "left")

	def display(self, data):
		self.status_label.config(text = data)	


# class rotationCuonter(tk.Frame):
# 	def __init__(self, parent):
# 		self.parent = parent

# 		self.bg = "azure3"
# 		self.highlightbackground = "gray30"
# 		self.highlightthickness = 1
# 		self.relief = "raised"
			
# 		self.width = 800
# 		self.height = 300


# 		tk.Frame.__init__(self, parent, width = self.width, height = self.height, bg = self.bg, bd = 1, highlightbackground = self.highlightbackground, highlightthickness = self.highlightthickness, relief = self.relief)
# 		self.pack_propagate(False)
# 		self.widgets()