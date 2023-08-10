from datetime import datetime
import os

def initialize_log_folder():
    dateTimeObj = datetime.now()
    dateTimeStr = str(dateTimeObj)
    logFileString = '/home/rsl/Desktop/logs/' + dateTimeStr 
    if os.path.isdir('/home/rsl/Desktop/logs'):
        logFile = open(logFileString, "x")
        logFile.close()
    else:
        os.mkdir('/home/rsl/Desktop/logs')
        logFile = open(logFileString, "x")
        logFile.close()
    #print(logFileString)
    return logFileString

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
