import serial
import datetime
import time
import threading
from PyQt5.QtWidgets import QApplication, QWidget

esp32 = serial.Serial('COM6',115200,timeout=.1)

def writeData(data): 
    time.sleep(1)
    esp32.write(data.encode())

#format X{ANGLE}Y{ANGLE}# 

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 800, 600)

    def mousePressEvent(self, event):
        #print("Mouse clicked at", event.x(), event.y())
        self.handle_mouse_click(event.x(),event.y())

    def handle_mouse_click(self,x,y):
        data = "X{}Y{}#".format(180 - ((x/1000)*180), (y/600)*180)
        writeData(data)
        print(data)

    


app = QApplication([])
widget = MyWidget()
widget.show()
app.exec_()
       


#ESP32 TO PYTHON 
# while True: 
#     data = esp32.readline()
#     if data: 
#         print(data)

# #PYTHON TO ESP32 
#     esp32.write("HELLO FROM PYTHON".encode())