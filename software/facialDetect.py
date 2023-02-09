

import cv2
import urllib.request 
import requests 
from urllib.request import urlopen
import urllib
import numpy as np
 
import serial
import datetime
import time
import threading


esp32 = serial.Serial('COM6',115200,timeout=.1)
f_cas= cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
eye_cascade=cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_eye.xml')
url='http://192.168.2.41/800x600.jpg'
##'''cam.bmp / cam-lo.jpg /cam-hi.jpg / cam.mjpeg '''
#cv2.namedWindow("Live Transmission", cv2.WINDOW_AUTOSIZE)
path = r'C:\Users\Ku\Documents\the nerd folder\Dwight\DWIGHT-The-watergun-alarm\software\1.png'

openCamera = False
#default is the center of the screen 
x_point = 400
y_point = 300 


def readUrl(): 
    data = esp32.readline() 
    data_str = data.decode()
    if ("https://" in data_str): 
        url = data_str
        print(url) 
        return True

def writeData(data):  
    time.sleep(1)
    esp32.write(data.encode())

print("Hello world")
while True:

   
    #'http://192.168.2.41/800x600.jpg' 
    req = urllib.request.urlopen('http://192.168.2.41/800x600.jpg')
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1) # 'Load it as it is'
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face=f_cas.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5)
    for x,y,w,h in face:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255),3)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        x_point = x + (w/2)
        y_point = y + (h/2)
        data = "X{}Y{}#".format(180 - ((x_point/1000)*180), (y_point/600)*180) 
        writeData(data)
        print(data)
        # eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex,ey,ew,eh) in eyes:
        #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    
    cv2.imshow('Video', img)




    # img_resp=urllib.request.urlopen(url)
    # imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    # img=cv2.imdecode(imgnp,-1)
    # gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # face=f_cas.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5)
    # for x,y,w,h in face:
    #     cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),3)
    #     roi_gray = gray[y:y+h, x:x+w]
    #     roi_color = img[y:y+h, x:x+w]
    #     eyes = eye_cascade.detectMultiScale(roi_gray)
    #     for (ex,ey,ew,eh) in eyes:
    #         cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
 
 
    #cv2.imshow("live transmission",img)
    key=cv2.waitKey(5)
    if key==ord('q'):
        break
 
cv2.destroyAllWindows()