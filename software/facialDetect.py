
import math
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
#haarcascade_frontalface_default.xml
f_cas= cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_alt.xml')
eye_cascade=cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_eye.xml')
url='http://192.168.2.41/800x600.jpg'
##'''cam.bmp / cam-lo.jpg /cam-hi.jpg / cam.mjpeg '''
#cv2.namedWindow("Live Transmission", cv2.WINDOW_AUTOSIZE)
path = r'C:\Users\Ku\Documents\the nerd folder\Dwight\DWIGHT-The-watergun-alarm\software\1.png'

openCamera = False
#default is the center of the screen 
x_point = 400
y_point = 300 
x_angle = 0 
y_angle = 90 
#distance measured in cm 
distance = 150
conversionFactor = 100
i = 45
switch = False; 

def readUrl(): 
    data = esp32.readline() 
    data_str = data.decode()
    if ("https://" in data_str): 
        url = data_str
        print(url) 
        return True

def writeData(data):  
    esp32.write(data.encode())

print("Hello world")

time.sleep(5)
data = "X{}Y{}Z{}#".format(93, 90, 0) 
writeData(data)
time.sleep(5)

while True:

    #'http://192.168.2.41/800x600.jpg' 
    req = urllib.request.urlopen('http://192.168.2.41/800x600.jpg')
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1) # 'Load it as it is'
    #img = cv2.flip(img,0); #verticle flip 
    img = cv2.rotate(img,rotateCode=1)
    

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #Make img lighter  
    alpha = 1.5 
    beta = 18
   
   
    #gray = cv2.addWeighted(gray, alpha, np.zeros(gray.shape, gray.dtype),beta,20)

    
    #1.1, 5 
    face=f_cas.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5, minSize=(50,50))
    for x,y,w,h in face:
        cv2.rectangle(gray,(x,y),(x+w,y+h),(0,255,255),3)
        #this is for eye detection within facial detection -> might be useful for mouth
        #roi_gray = gray[y:y+h, x:x+w] #Croping 
        #roi_color = img[y:y+h, x:x+w]
        # x_point = (x + (w/2))/800 * conversionFactor
        # y_point = (y + (h/2))/600 * conversionFactor 

        x_point = x + (w/2) - 400 
        y_point = y + (y/2) - 300
        x_angle  = 90 + math.degrees(math.atan((x_point)/distance))
        y_angle = 90 + math.degrees(math.atan((y_point)/distance))

        print("X{}Y{}Z{}#".format(x_angle, y_angle, 0)) 
        data = "X{}Y{}Z{}#".format(x_angle, y_angle, 0)
        writeData(data)
        # eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex,ey,ew,eh) in eyes:
        #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    

    cv2.imshow('Video', gray)
    writeData(data)
    key=cv2.waitKey(5)
    if key==ord('q'):
        break
 
cv2.destroyAllWindows()