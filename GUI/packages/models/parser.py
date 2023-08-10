def parse(string, data):
	#string is the input nmea string
	#data is a Data class to put parsed data in

	#tokenize

	values = string.split(",")

	if values[0] != "$" and values[5] != "*":
		return 

	data.assign("ID", values[1])

	data.assign("TMPR", values[2])

	data.assign("PRES", values[3])
	
	data.assign("HEAD", values[4])
