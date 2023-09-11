# file: graphs.py
# description: creates and maintains the graphs on the GUI

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib import style
from datetime import datetime
from collections import deque

#matplotlib.rcParams.update({'font.size': 60})

style.use('ggplot')
#set(0,'defaultTextFontName','Courier')

starttime = datetime.now()
refresh_rate = 20

alt = 0
dpth = 0
head = 0
time = 0

alt_prev = 0
dpth_prev = 0
head_prev = 0
time_prev = 0

figure, (alt_subplot, dpth_subplot, head_subplot) = plt.subplots(3)

figure.suptitle('Sensor Data')
alt_subplot.set_title('Altitude (m)', y = 1)
dpth_subplot.set_title('Depth (m)', y = 1)
head_subplot.set_title('Heading (deg)', y = 1)

plt.subplots_adjust(hspace = 0.7)

alt_subplot.set_xlabel('time (s)')
dpth_subplot.set_xlabel('time (s)')
head_subplot.set_xlabel('time (s)')

a_line, = alt_subplot.plot(0, 0, color = "blue")
d_line, = dpth_subplot.plot(0, 0, color = "red")
h_line, = head_subplot.plot(0, 0, color = "black")

max_length = 10



def update_data(field, data):
	global alt, dpth, head

	if field == "ALT":
		alt = data

	elif field == "DEPTH":
		dpth = data

	elif field == "HEAD":
		head = data



def plot(interval):
	global time_prev, alt_prev, dpth_prev, head_prev

	time = (datetime.now() - starttime).total_seconds()

	time_list = [time_prev, time]
	alt_list = [alt_prev, alt]
	dpth_list = [dpth_prev, dpth]
	head_list = [head_prev, head]

	alt_subplot.plot(time_list, alt_list, color = "blue")
	dpth_subplot.plot(time_list, dpth_list, color = "red")
	head_subplot.plot(time_list, head_list, color = "black")

	time_prev = time
	alt_prev = alt
	dpth_prev = dpth
	head_prev = head

	# If the current time is divisible by the refresh rate, clear the graphs. Q: When this happens, we lose titles
	if(round(time) % refresh_rate == 0):
		cleargraphs()



def cleargraphs():
	alt_subplot.cla()
	dpth_subplot.cla()
	head_subplot.cla()



def animate(interval):
	return animation.FuncAnimation(figure, plot, interval=interval)



def figure_canvas(figure, parent):
	return FigureCanvasTkAgg(figure, parent)


