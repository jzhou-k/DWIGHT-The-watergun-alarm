import serial
import datetime
import time
import threading
from PyQt5.QtWidgets import QApplication, QWidget




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
    time.sleep(1)
    arduino.write(data.encode())
    # *****READS DATA******
    # while True: 
    #     data = arduino.read().decode()
    #     if data: 
    #         #data = data.rstrip("#")
    #         print(data, end='')   

#format X{ANGLE}Y{ANGLE}# 

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)

    def mousePressEvent(self, event):
        #print("Mouse clicked at", event.x(), event.y())
        self.handle_mouse_click(event.x(),event.y())

    def handle_mouse_click(self,x,y):
        data = "X{}Y{}#".format(180-((x/800)*180), 180 - (y/600)*180)
        writeData(data)
        print(data)
        



app = QApplication([])
widget = MyWidget()
widget.show()
app.exec_()



#     #time.sleep(1)

# ***** START ALARM FUNCTION ***** 
# t1 = threading.Thread(target=alarmFunction)
# t1.start()
# t1.join()

#print("GOOD FUCKING MORNING")
#Python -> Arduino -> Python again 


