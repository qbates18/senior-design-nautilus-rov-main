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

tmpr_deque = deque()
pres_deque = deque()
head_deque = deque()
time_deque = deque()

tmpr_deque.append(0)
pres_deque.append(0)
head_deque.append(0)
time_deque.append(0)

figure, (tmpr_subplot, pres_subplot, head_subplot) = plt.subplots(3)

figure.suptitle('Sensor Data')
tmpr_subplot.set_title('Temperature (C)', y = 1)
pres_subplot.set_title('Pressure (mbar)', y = 1)
head_subplot.set_title('Heading (deg)', y = 1)

plt.subplots_adjust(hspace = 0.7)
# pres_subplot.subplots_adjust(hspace = 1)
# head_subplot.subplots_adjust(hspace = 1)

tmpr_subplot.set_xlabel('time (s)')
pres_subplot.set_xlabel('time (s)')
head_subplot.set_xlabel('time (s)')



max_length = 10


def update_data(field, data):
	if field == "TMPR":
		if len(tmpr_deque) >= max_length:
			time_deque.popleft()
			tmpr_deque.popleft()
		tmpr_deque.append(data)

		now = (datetime.now() - starttime).total_seconds()
		
		time_deque.append(now)
			
	elif field == "PRES":
		if len(pres_deque) >= max_length:
			pres_deque.popleft()
		pres_deque.append(data)

	elif field == "HEAD":
		if len(head_deque) >= max_length:
			head_deque.popleft()
		head_deque.append(data)




def plot(interval):

	time = np.array(list(time_deque))
	
	tmpr_subplot.plot(time, np.array(list(tmpr_deque)), color = "blue")

	pres_subplot.plot(time, np.array(list(pres_deque)), color = "red")

	head_subplot.plot(time, np.array(list(head_deque)), color = "black")

	


def animate(interval):
	return animation.FuncAnimation(figure, plot, interval=interval)


def figure_canvas(figure, parent):
	return FigureCanvasTkAgg(figure, parent)


