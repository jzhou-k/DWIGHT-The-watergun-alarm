import serial
import datetime
import time
import threading

arduino = serial.Serial('COM3', 115200, timeout=.1)
print("Helloworld")

#arduino to python and python interprets data 
# while True: 
#     data = arduino.readline()[:-2]
#     if data:
#         print(data)

# # wow chat gpt is very useful assistant ?

def alarmFunction():
    
    def countTime(stop_event): 
        #start = datetime.datetime.now()
        while not stop_event.is_set():
            #timeElapsed = datetime.datetime.now() - start
            print(datetime.datetime.now().strftime("%H:%M:%S"))
            stop_event.wait(1)

    # Get the current time
    now = datetime.datetime.now()
    stop_event = threading.Event()


    #TO actually enter the alarm time e.g 7:30 
    #This is the most dumb solution : ^) 
    #Parse string to hour min then pass into time delta, the day will be incremented automatically 
    # 'Wed Jun  9 04:26:40 1993'. standard format 
    alarmH = 13
    alarmM = 30 
    nowH = (int)(now.strftime("%H"))
    nowM = (int)(now.strftime("%M"))

    diffH = alarmH - nowH 
    diffM = alarmM - nowM 

    elapseH  = 0 
    elapseM = 0
    
    if(diffH < 0 or (diffH == 0 and diffM < 0)): 
        elapseH = 23 + diffH 
        elapseM = 60 + diffM
        print("{}:{}".format(elapseH,elapseM))
    elif (diffM < 0): 
        elapseH = diffH - 1
        elapseM = 60 + diffM
        print("{}:{}".format(elapseH,elapseM))
    else:
        elapseH = diffH 
        elapseM = diffM 
        print("{}:{}".format(elapseH,elapseM))



    # Calculate the alarm time (10 minutes from now)
    alarm_time = now + datetime.timedelta(hours=elapseH, minutes=elapseM)

    #Start displayin time elapsed thread 
    t2 = threading.Thread(target=countTime, args=(stop_event, ))
    t2.start()

    # Sleep until the alarm time
    time.sleep((alarm_time - now).total_seconds())

    # Alarm goes off
    print("Wake up!")
    stop_event.set()

def writeData(data): 
    time.sleep(2)
    arduino.write(data.encode())
    while True: 
        data = arduino.read().decode()
        if data: 
            #data = data.rstrip("#")
            print(data, end='')   

writeData("X25Y25#")

# ***** START ALARM FUNCTION ***** 
# t1 = threading.Thread(target=alarmFunction)
# t1.start()
# t1.join()

#print("GOOD FUCKING MORNING")
#Python -> Arduino -> Python again 


