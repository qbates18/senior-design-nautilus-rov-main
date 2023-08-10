import serial
import time

ard = serial.Serial('/dev/ttyACM0',11520,timeout=6)

while(1):
    msg_utf = ard.readline()
    msg=str(msg_utf)
    print(msg_utf)
    print(msg)





## Write ping with numbers counting up
#msg="ping "
#i=0
#while(1):
#    msg="ping " + str(i)
#    msg_utf=msg.encode(encoding='ascii')
#    ard.write(msg_utf)
#    #print(msg)
#    time.sleep(1)
#    i += 1