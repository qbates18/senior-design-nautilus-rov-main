# file: data_log.py
# description: creates a log folder for each Nautilus deployment automatically, logging the messages sent back and forth between topside and subsea

from datetime import datetime
import os

timeDeploymentStarted = datetime.now() #universal source of truth for the start time of the deployment, to import use from imports import timeDeploymentStarted
timeVideoStarted = None #universal source of truth for the start time of the video, to import use from imports import timeVideoStarted

# funciton: initialize_log_folder()
# description: creates a unique folder to store logs, intended to be ran each time the GUI is launched
def initialize_log_folder():
    dateTimeObj = timeDeploymentStarted
    dateTimeStr = str(dateTimeObj)
    logFileString = '/home/rsl/Desktop/logs/' + dateTimeStr 
    if os.path.isdir('/home/rsl/Desktop/logs'):
        logFile = open(logFileString, "x")
        logFile.close()
    else:
        os.mkdir('/home/rsl/Desktop/logs')
        logFile = open(logFileString, "x")
        logFile.close()
    return logFileString


# function: write_to_log()
# description: write a message to log, intended to be run for each sent/recieved message
def write_to_log(input_string, log_file):
    #take system time
    dateTimeObj = datetime.now()
    dateTimeStr = str(dateTimeObj) + "  "
    
    #open file
    f = open(str(log_file), "a")
    #write system time
    f.write(dateTimeStr)
    #write input_string
    f.write(input_string)
    #write new line
    f.write("\n")
    #close file
    f.close()

if __name__ == "__main__":
    initialize_log_folder()
