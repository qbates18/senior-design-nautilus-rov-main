#Q: Is this obsolete? passing the NMEA string is currently all handled in main.py and ROS is no longer used

import socket	

def socket_send(data, s):

	# send GUI NMEA string
	s.send(data.encode())

	# receive/print ROS response over socket
	print(s.recv(1024).decode())


