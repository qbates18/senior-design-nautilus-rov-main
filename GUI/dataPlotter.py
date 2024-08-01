import sys
import heapq as hq
import datetime

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

### HOW TO USE ###
# This code is a visualizer for Nautilus and uses the log files generated in it to visualize the output data.
# This code is heavily dependent on the precise formatting of those files (as controlled by generator.py and Neptune.cpp)
# Thie code is accurate as of April 2024 with the following standards:
# Messages passed from Nautilus happen in the format:
# YYYY-MM-DD HH:MM:SS.xxxxxx  b'\r\n$, messageId, temperature, depth, heading, altitude, leak, voltage, *'
# Where messageId is an integer and all following values are represented as floats (although * is a literal *)
# Messages sent to Nautilus cannot begin with this same signature (b'\r\n)
# Captain's Log files are determiend as any file ending with "Captains Log.txt"--please make sure they follow this format.
# All other files will be examined as data log files and can have any name.
# Captain's Log entries need to be formatted where text entries start with Captain's Log Entry on one line, the following line starts with YYYY-MM-DD HH:MM:SS
# Then one line is alloted for data values to be printed (ignored) and the comments will be considered to start on the following line.
# All different entries should be separated by exactly two newlines.
# Set points also need to start with the same time formatting and should announce their type starting at index 54 using the terms "Depth control" "Heading control" or "Altitude control"
# Set points need " set to " in order to find the specific value of the set point, if off should state "Off". Nothing should follow the Off or value.


# Parses messages to identify those that are from Nautilus, returns the data values in a list as either integers or floats.
def stringParser(message):
	if message[0:6] != "b'\\r\\n":
		return None
	try:
		result = message.split(', ')
		result[1] = int(result[1]) # message ID
		result[2] = float(result[2]) # temperature
		result[3] = float(result[3]) # depth
		result[4] = float(result[4]) # heading
		result[5] = float(result[5]) # altitude
		result[6] = float(result[6]) # leak
		result[7] = float(result[7]) # voltage
		return result[1:8] # only returns the subset of the list between indexes 1 and 7 (inclusive)
	except:
		return None


# Uses stringParser() to go through every line in a file (open file with read access passed in as f) 
# Returns startTime (the smallest timestamp associated with a message containing sensor data) and equally-sized lists of timestamps, depths, altitudes, and headings
def logFileParser(f):
	times = list()
	depths = list()
	alts = list()
	headings = list()
	startTime = None
	for line in f:
		components = line.split(' ', 3)
		time = datetime.datetime.strptime(components[0] + " " + components[1], '%Y-%m-%d %H:%M:%S.%f')
		parsedValues = stringParser(components[3])
		if parsedValues != None:
			if startTime == None or time < startTime:
				startTime = time
			#print(time.strftime('%H:%M:%S') + "\t(Depth:" + str(parsedValues[2]) + ", Altitude:" + str(parsedValues[4]) + ", Heading:" + str(parsedValues[3]) + ')')
			times.append(time)
			depths.append(parsedValues[2])
			alts.append(parsedValues[4])
			headings.append(parsedValues[3])
	return startTime, times, depths, alts, headings


def captainsLogParser(f):
	f = open(f, "r", encoding='utf-8')
	logText = f.read()
	logText = logText.strip()
	logLines = logText.split("\n\n") # separates all entries (cannot only use one line due to multiline data)
	pq = list()
	depthSP = SetPoints()
	altSP = SetPoints()
	headSP = SetPoints()
	for entry in logLines:
		if entry[0:19] == "Captain's Log Entry":
			lines = entry.split("\n", 3)
			timestamp = datetime.datetime.strptime(lines[1][0:19], '%Y-%m-%d %H:%M:%S')
			hq.heappush(pq, (timestamp, lines[3]))
		elif entry[54:67] == "Depth control":
			value = entry.split(" set to ")
			timestamp = datetime.datetime.strptime(value[0][0:19], '%Y-%m-%d %H:%M:%S')
			if value[1] == "Off":
				depthSP.off(timestamp)
			else:
				value = value[1].split(',', 1)
				DepthGainsValues = value[1].strip()
				DepthGainsValues = DepthGainsValues.split()
				DepthGainsValues = [DepthGainsValues[3][3:], DepthGainsValues[4][3:], DepthGainsValues[5][3:]]
				print("DepthGainsValues:")
				print(DepthGainsValues)
				depthSP.on(timestamp, float(value[0]))
		elif entry[54:70] == "Altitude control":
			value = entry.split(" set to ")
			timestamp = datetime.datetime.strptime(value[0][0:19], '%Y-%m-%d %H:%M:%S')
			if value[1] == "Off":
				altSP.off(timestamp)
			else:
				value = value[1].split(',', 1)
				AltitudeGainsValues = value[1].strip()
				AltitudeGainsValues = AltitudeGainsValues.split()
				AltitudeGainsValues = [AltitudeGainsValues[3][3:], AltitudeGainsValues[4][3:], AltitudeGainsValues[5][3:]]
				print("AltitudeGainsValues:")
				print(AltitudeGainsValues)
				altSP.on(timestamp, float(value[0]))
		elif entry[54:69] == "Heading control":
			value = entry.split(" set to ")
			timestamp = datetime.datetime.strptime(value[0][0:19], '%Y-%m-%d %H:%M:%S')
			if value[1] == "Off":
				headSP.off(timestamp)
			else:
				value = value[1].split(',', 1)
				HeadingGainsValues = value[1].strip()
				HeadingGainsValues = HeadingGainsValues.split()
				HeadingGainsValues = [HeadingGainsValues[3][3:], HeadingGainsValues[4][3:], HeadingGainsValues[5][3:]]
				print("HeadingGainsValues:")
				print(HeadingGainsValues)
				headSP.on(timestamp, float(value[0]))
		else:
			print("No match!")

	f.close()
	dtimes, depths = depthSP.getValues()
	atimes, alts = altSP.getValues()
	htimes, heads = headSP.getValues()
	return dtimes, depths, atimes, alts, htimes, heads, pq


# Helper class to handle the data structures, preserves data as a list of lists and as one list of all the data points
class Data():
	def __init__(self):
		self.dataCollections = list()
		self.data = list()
	
	def add(self, data):
		self.dataCollections = self.dataCollections + [data]
		self.data = self.data + data

	def getCollections(self):
		return self.dataCollections
	
	def getOneList(self):
		return self.data
	
	# Adjusts the lists to relative time (assuming they are datetime objects) based on the starting time passed in
	def makeRelativeTime(self, startTime):
		self.dataCollections= [[(time - startTime).total_seconds() for time in timeSet] for timeSet in self.dataCollections]
		self.data = [(time - startTime).total_seconds() for time in self.data]


# Helper class to handle setpoints - do not pass string values
class SetPoints():
	def __init__(self):
		self.times = list()
		self.values = list()

	def on(self, time, value):
		self.startTime = time
		self.val = value

	def off(self, endTime):
		self.times = self.times + [[self.startTime, endTime]]
		self.values = self.values + [[self.val, self.val]]
		self.startTime = None
		self.val = None

	def getValues(self):
		return self.times, self.values


# Generates all the graphs, only displays one canvas at a time using a QStackedLayout
# Currently displayed item can be changed using setCurrentIndex
class Graphs(QWidget):
	def __init__(self, times, depths, alts, headings):
		super(Graphs, self).__init__()
		plt.style.use('seaborn-v0_8-colorblind')
		self.stack = QStackedLayout()
		self.setLayout(self.stack)
		self.visibleAvg = True
		self.visibleData = True
		self.times = times
		self.depths = depths
		self.alts = alts
		self.headings = headings

		# Calculates the rolling averages (with a window size of 10) for depth, altitude, and heading
		df = DataFrame(self.depths.getOneList())
		avgDepths = df.rolling(window=10).mean()
		df = DataFrame(self.alts.getOneList())
		avgAlts = df.rolling(window=10).mean()
		df = DataFrame(self.headings.getOneList())
		avgHeads = df.rolling(window=10).mean()

		# Need to have one canvas and one entry in rawLines for each entry in the stack
		self.canvas = (FigureCanvas(Figure(figsize=(5, 5))), FigureCanvas(Figure(figsize=(5, 5))), FigureCanvas(Figure(figsize=(5, 5))), FigureCanvas(Figure(figsize=(5, 5))), FigureCanvas(Figure(figsize=(5, 5))))
		self.rawLines = [[], [], [], [], []]

		# Initializes canvas[0] which will contain 3 separate graphs (one for depth, one for heading, one for altitude)
		self.depth_ax0, self.alt_ax0, self.heading_ax0 = self.canvas[0].figure.subplots(3,1,sharex='all')
		for timeSet, depthSet in zip(self.times.getCollections(), self.depths.getCollections()):
			line, = self.depth_ax0.plot(timeSet, depthSet)
			self.rawLines[0].append(line)
		for timeSet, altSet in zip(self.times.getCollections(), self.alts.getCollections()):
			line, = self.alt_ax0.plot(timeSet, altSet)
			self.rawLines[0].append(line)
		for timeSet, headSet in zip(self.times.getCollections(), self.headings.getCollections()):
			line, = self.heading_ax0.plot(timeSet, headSet)
			self.rawLines[0].append(line)
		avg0, = self.depth_ax0.plot(self.times.getOneList(), avgDepths, 'darkorchid')
		avg1, = self.alt_ax0.plot(self.times.getOneList(), avgAlts, 'darkorchid')
		avg2, = self.heading_ax0.plot(self.times.getOneList(), avgHeads, 'darkorchid')
		self.depth_ax0.set_ylabel("Depth (m)")
		self.depth_ax0.invert_yaxis()
		self.depth_ax0.set_ylim(None, 0)
		self.alt_ax0.set_ylabel("Altitude (m)")
		self.alt_ax0.invert_yaxis()
		self.heading_ax0.set_ylabel("Heading")
		self.heading_ax0.set_xlabel("Time (s)")
		self.depth_ax0.set_title("Dive Overview")

		# Initializes canvas[1] which contains 3 different data collections on one graph--depth, altitude, and the sum of depth and altitude
		# TODO - rolling average of water depth
		self.DALines = list()
		self.ax1 = self.canvas[1].figure.subplots()
		for timeSet, depthSet, altSet in zip(self.times.getCollections(), self.depths.getCollections(), self.alts.getCollections()):
			line, = self.ax1.plot(timeSet, depthSet, 'blue')
			self.DALines.append(line)
			self.rawLines[1].append(line)
			line, = self.ax1.plot(timeSet, altSet, 'green')
			self.DALines.append(line)
			self.rawLines[1].append(line)
			waterDepth = [depth + alt for depth, alt in zip(depthSet, altSet)]
			self.ax1.plot(timeSet, waterDepth, 'purple')
		self.ax1.legend(['Depth', 'Altitude', 'Est. Water Depth']) # this setup relies upon the first three lines being one depth, one altitude, and one est. water depth in that order
		self.ax1.set_ylabel("Depth/Altitude (m)")
		self.ax1.invert_yaxis()
		self.ax1.set_ylim(None, 0)
		self.ax1.set_xlabel("Time (s)")
		self.ax1.set_title("Depth of Dive")

		# Initializes canvas[2] which contains 1 graph plotting depth over time
		self.ax2 = self.canvas[2].figure.subplots()
		for timeSet, depthSet in zip(self.times.getCollections(), self.depths.getCollections()):
			line, = self.ax2.plot(timeSet, depthSet)
			self.rawLines[2].append(line)
		avg3, = self.ax2.plot(self.times.getOneList(), avgDepths, 'darkorchid')
		self.ax2.set_ylabel("Depth (m)")
		self.ax2.invert_yaxis()
		self.ax2.set_ylim(None, 0)
		self.ax2.set_xlabel("Time (s)")
		self.ax2.set_title("Depth of Dive")

		# Initializes canvas[3] which contains 1 graph plotting altitude over time
		self.ax3 = self.canvas[3].figure.subplots()
		for timeSet, altSet in zip(self.times.getCollections(), self.alts.getCollections()):
			line, = self.ax3.plot(timeSet, altSet)
			self.rawLines[3].append(line)
		avg4, = self.ax3.plot(self.times.getOneList(), avgAlts, 'darkorchid')
		self.ax3.set_ylabel("Altitude (m)")
		self.ax3.invert_yaxis()
		self.ax3.set_ylim(None, 0)
		self.ax3.set_xlabel("Time (s)")
		self.ax3.set_title("Altitude of Dive")

		# Initializes canvas[4] which contains 1 graph plotting heading over time
		self.ax4 = self.canvas[4].figure.subplots()
		for timeSet, altSet in zip(self.times.getCollections(), self.headings.getCollections()):
			line, = self.ax4.plot(timeSet, altSet)
			self.rawLines[4].append(line)
		avg5, = self.ax4.plot(self.times.getOneList(), avgHeads, 'darkorchid')
		self.ax4.set_ylabel("Heading")
		self.ax4.set_xlabel("Time (s)")
		self.ax4.set_title("Heading of Dive")

		self.averages = ([avg0, avg1, avg2], [], [avg3], [avg4], [avg5])
		self.MakeAveragesInvisible(0)

		for canvas in (self.canvas):
			widget = QWidget()
			lay = QVBoxLayout(widget)
			lay.addWidget(NavigationToolbar(canvas))
			lay.addWidget(canvas)
			self.stack.addWidget(widget)

	def getCurrentIndex(self):
		return self.stack.currentIndex()

	# Updates what is currently visible in the stack and makes necessary changes before loading the new index
	def setCurrentIndex(self, index):
		if self.visibleAvg:
			self.MakeAveragesVisible(index)
		else:
			self.MakeAveragesInvisible(index)

		if self.visibleData:
			self.RawDataOn(index)
		else:
			self.RawDataOff(index)

		return self.stack.setCurrentIndex(index)

	def RawDataOn(self, index=None):
		if index is None:
			index = self.getCurrentIndex()
		for line in self.rawLines[index]:
			line.set_linestyle('solid')
		self.canvas[index].draw()
		self.visibleData = True

	def RawDataOff(self, index=None):
		if index is None:
			index = self.stack.currentIndex()
		for line in self.rawLines[index]:
			line.set_linestyle('none')
		self.canvas[index].draw()
		self.visibleData = False

	def MakeAveragesVisible(self, index=None):
		if index is None:
			index = self.getCurrentIndex()
		for line in self.averages[index]:
			line.set_linestyle('solid')
		self.canvas[index].draw()
		self.visibleAvg = True

	def MakeAveragesInvisible(self, index=None):
		if index is None:
			index = self.stack.currentIndex()
		for line in self.averages[index]:
			line.set_linestyle('none')
		self.canvas[index].draw()
		self.visibleAvg = False

	def addSetpoints(self, depths, depthTimes, alts, altTimes, heads, headTimes):
		self.setpointLines = list()
		for times, d in zip(depthTimes, depths):
			line, = self.depth_ax0.plot(times, d, 'red', linestyle="--")
			self.setpointLines.append(line)
			line, = self.ax2.plot(times, d, 'red', linestyle="--")
			self.setpointLines.append(line)
		for times, a in zip(altTimes, alts):
			line, = self.alt_ax0.plot(times, a, 'red', linestyle="--")
			self.setpointLines.append(line)
			line, = self.ax3.plot(times, a, 'red', linestyle="--")
			self.setpointLines.append(line)
		for times, h in zip(headTimes, heads):
			line, = self.heading_ax0.plot(times, h, 'red', linestyle="--")
			self.setpointLines.append(line)
			line, = self.ax4.plot(times, h, 'red', linestyle="--")
			self.setpointLines.append(line)

	def SetpointsOff(self, index=None):
		for line in self.setpointLines:
			line.set_linestyle('none')
		for canvas in (self.canvas):
			canvas.draw()

	def SetpointsOn(self, index=None):
		for line in self.setpointLines:
			line.set_linestyle('--')
		for canvas in (self.canvas):
			canvas.draw()

	def WaterDepthOnly(self):
		for line in self.DALines:
			line.set_linestyle('none')
		self.canvas[1].draw()

	def WaterDepthOnlyOff(self):
		for line in self.DALines:
			line.set_linestyle('solid')
		self.canvas[1].draw()


class MainWindow(QWidget):
	def __init__(self, args):
		super(MainWindow, self).__init__()
		self.setWindowTitle('Nautilus Trip Visualizer')
		self.layout = QGridLayout()
		self.setLayout(self.layout)

		# Check for parseable data
		if (len(args) == 1):
			self.text = QLabel()
			self.layout.addWidget(self.text)
			self.text.setText("Please pass any logs file as command line input.")
			return
		
		# Parse all the data and put it into self.times, self.depths, self.alts, self.headings. and self.startTime--the first four will all be lists of lists of floats for plotting
		self.times = Data()
		self.depths = Data()
		self.alts = Data()
		self.headings = Data()
		self.startTime = None
		self.depthTargetTimes = list()
		self.depthTargets = list()
		self.altTargetTimes = list()
		self.altTargets = list()
		self.headTargetTimes = list()
		self.headTargets = list()
		self.logEntry = list()
		logEntryText = ""

		for filename in args[1:]:
			if filename[-16:] == "Captains Log.txt":
				depthTargetTimes, depthTargets, altTargetTimes, altTargets, headTargetTimes, headTargets, logEntry = captainsLogParser(filename) 
				self.depthTargetTimes = self.depthTargetTimes + depthTargetTimes
				self.depthTargets = self.depthTargets + depthTargets
				self.altTargetTimes = self.altTargetTimes + altTargetTimes
				self.altTargets = self.altTargets + altTargets
				self.headTargetTimes = self.headTargetTimes + headTargetTimes
				self.headTargets = self.headTargets + headTargets
				self.logEntry = hq.merge(self.logEntry, logEntry)
			else:
				f = open(filename, "r")
				st, t, d, a, h =  logFileParser(f)

				# Maintains startTime to be the absolute earliest time
				if self.startTime == None or st < self.startTime:
					self.startTime = st
				self.times.add(t)
				self.depths.add(d)
				self.alts.add(a)
				self.headings.add(h)
				f.close()

		self.times.makeRelativeTime(self.startTime)
		self.depthTargetTimes = [[(time - self.startTime).total_seconds() for time in timeSet] for timeSet in self.depthTargetTimes]
		self.altTargetTimes = [[(time - self.startTime).total_seconds() for time in timeSet] for timeSet in self.altTargetTimes]
		self.headTargetTimes = [[(time - self.startTime).total_seconds() for time in timeSet] for timeSet in self.headTargetTimes]
		i = 1
		for (time, text) in self.logEntry:
			logEntryText = logEntryText + "--- Entry " + str(i) + " at " + str(int((time - self.startTime).total_seconds())) + " s ---\n" + text + "\n\n"
			i+=1
		logEntryText = logEntryText.strip()

		# Submenu for Graph Settings
		submenu = QVBoxLayout()
		prompt = QLabel()
		prompt.setText("Select your graph view:")
		submenu.addWidget(prompt)
		self.graphType = QComboBox()
		# The names chosen can be edited, but the relative ordering must stay the same as it uses their relative frequencies.
		self.graphType.addItems(['Trip Overview (Depth, Altitude, and Heading)', 'Depth and Altitude', 'Depth', 'Altitude', 'Heading'])
		submenu.addWidget(self.graphType)

		self.rawData = QCheckBox()
		self.rawData.setText("See Raw Data")
		self.rawData.setChecked(True)
		submenu.addWidget(self.rawData)

		self.filter = QCheckBox()
		self.filter.setText("See Moving Averages")
		submenu.addWidget(self.filter)

		self.seeSets = QCheckBox()
		self.seeSets.setText("See Setpoints")
		self.seeSets.setChecked(True)
		submenu.addWidget(self.seeSets)

		self.sumOnly = QCheckBox()
		self.sumOnly.setText("Only See Water Depth")
		submenu.addWidget(self.sumOnly)

		logTitle = QLabel()
		logTitle.setText("Captain's Log Notes:",)
		submenu.addWidget(logTitle)
		logText = QTextEdit()
		logText.setText(logEntryText)
		logText.setReadOnly(True)
		logText.setMaximumHeight(500)
		submenu.addWidget(logText)

		submenu.addStretch() # consumes as much space on the bottom as possible
		self.layout.setColumnStretch(0,1) # prioritizes making the graphs bigger rather than the menu

		self.graphs = Graphs(self.times, self.depths, self.alts, self.headings)
		self.graphs.addSetpoints(self.depthTargets, self.depthTargetTimes, self.altTargets, self.altTargetTimes, self.headTargets, self.headTargetTimes)

		self.layout.addWidget(self.graphs, 0, 0)
		self.layout.addLayout(submenu,0,1)
		self.graphType.activated.connect(self.graphs.setCurrentIndex)
		self.rawData.stateChanged.connect(self.toggleRawData)
		self.filter.stateChanged.connect(self.toggleGraphs)
		self.seeSets.stateChanged.connect(self.toggleSetpoints)
		self.sumOnly.stateChanged.connect(self.toggleWaterDepth)

	def toggleRawData(self):
		if self.rawData.isChecked():
			self.graphs.RawDataOn()
		else:
			self.graphs.RawDataOff()

	def toggleGraphs(self):
		if self.filter.isChecked():
			self.graphs.MakeAveragesVisible()
		else:
			self.graphs.MakeAveragesInvisible()

	def toggleSetpoints(self):
		if self.seeSets.isChecked():
			self.graphs.SetpointsOn()
		else:
			self.graphs.SetpointsOff()

	def toggleWaterDepth(self):
		if self.sumOnly.isChecked():
			self.graphs.WaterDepthOnly()
		else:
			self.graphs.WaterDepthOnlyOff()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = MainWindow(sys.argv)
	gui.show()
	sys.exit(app.exec_())