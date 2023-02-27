#Alarm function 
#Face detect function loop 
#Better aiming calibration 
#Additional functions 
#Mouth aiming
#Head aiming 
#Camera and turret targeting 
#Embedded and serial communication 
#Solidworks 

#Finger tracking 
#whole hand for stop
#middle finger detection then more shooting 
#rock sign to aim at mouth 
import math
import urllib.request
import requests
from urllib.request import urlopen
import urllib

import serial
import datetime
import time
import threading
import argparse
import os 

import numpy as np
import cv2 as cv

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import QDesktopWidget

from yunet import YuNet

from playsound import playsound

def str2bool(v):
    if v.lower() in ['on', 'yes', 'true', 'y', 't']:
        return True
    elif v.lower() in ['off', 'no', 'false', 'n', 'f']:
        return False
    else:
        raise NotImplementedError


backends = [cv.dnn.DNN_BACKEND_OPENCV, cv.dnn.DNN_BACKEND_CUDA]
targets = [cv.dnn.DNN_TARGET_CPU,
           cv.dnn.DNN_TARGET_CUDA, cv.dnn.DNN_TARGET_CUDA_FP16]
help_msg_backends = "Choose one of the computation backends: {:d}: OpenCV implementation (default); {:d}: CUDA"
help_msg_targets = "Choose one of the target computation devices: {:d}: CPU (default); {:d}: CUDA; {:d}: CUDA fp16"
try:
    backends += [cv.dnn.DNN_BACKEND_TIMVX]
    targets += [cv.dnn.DNN_TARGET_NPU]
    help_msg_backends += "; {:d}: TIMVX"
    help_msg_targets += "; {:d}: NPU"
except:
    print('This version of OpenCV does not support TIM-VX and NPU. Visit https://github.com/opencv/opencv/wiki/TIM-VX-Backend-For-Running-OpenCV-On-NPU for more information.')


parser = argparse.ArgumentParser(
    description='YuNet: A Fast and Accurate CNN-based Face Detector (https://github.com/ShiqiYu/libfacedetection).')
parser.add_argument('--input', '-i', type=str,
                    help='Usage: Set input to a certain image, omit if using camera.')
parser.add_argument('--model', '-m', type=str, default='face_detection_yunet_2022mar.onnx',
                    help="Usage: Set model type, defaults to 'face_detection_yunet_2022mar.onnx'.")
parser.add_argument('--backend', '-b', type=int,
                    default=backends[0], help=help_msg_backends.format(*backends))
parser.add_argument('--target', '-t', type=int,
                    default=targets[0], help=help_msg_targets.format(*targets))
parser.add_argument('--conf_threshold', type=float, default=0.9,
                    help='Usage: Set the minimum needed confidence for the model to identify a face, defauts to 0.9. Smaller values may result in faster detection, but will limit accuracy. Filter out faces of confidence < conf_threshold.')
parser.add_argument('--nms_threshold', type=float, default=0.3,
                    help='Usage: Suppress bounding boxes of iou >= nms_threshold. Default = 0.3.')
parser.add_argument('--top_k', type=int, default=5000,
                    help='Usage: Keep top_k bounding boxes before NMS.')
parser.add_argument('--save', '-s', type=str, default=True,
                    help='Usage: Set “True” to save file with results (i.e. bounding box, confidence level). Invalid in case of camera input. Default will be set to “False”.')
parser.add_argument('--vis', '-v', type=str2bool, default=True,
                    help='Usage: Default will be set to “True” and will open a new window to show results. Set to “False” to stop visualizations from being shown. Invalid in case of camera input.')
# Used to control turret movment
parser.add_argument('--controlMode', type=str, default="alarm",
                    help='Usage: manual: Control coord with mouse click, alarm: alarmMode with face detection')
parser.add_argument('--alarmTime', type=str, default = "8:30",
                    help='Usage: will allow for user input for alarm time')
args = parser.parse_args()

esp32 = serial.Serial('COM3',115200,timeout=.1)
def writeData(data):
    esp32.write(data.encode())
    print(data)

#Alarm setting better way of setting alarm bruh 
def alarmFunction(h,m):
    
    def countTime(stop_event): 
        time.sleep(5);
        writeData("{}:{}:0#".format(h,m))
        time.sleep(10) #waits for 10 sec for oled to set up 

        #start = datetime.datetime.now()
        while not stop_event.is_set():
            #timeElapsed = datetime.datetime.now() - start prints minutes 
            timeNow = datetime.datetime.now().strftime("%H:%M:%S")
            
            timeNow = timeNow + "#"
            writeData(timeNow)
            stop_event.wait(1)


    # Get the current time
    now = datetime.datetime.now()
    stop_event = threading.Event()


    #TO actually enter the alarm time e.g 7:30 
    #This is the most dumb solution : ^) 
    #Parse string to hour min then pass into time delta, the day will be incremented automatically 
    # 'Wed Jun  9 04:26:40 1993'. standard format 
    alarmH = int(h)
    alarmM = int(m)
    nowH = (int)(now.strftime("%H"))
    nowM = (int)(now.strftime("%M"))

    diffH = alarmH - nowH 
    diffM = alarmM - nowM 
    print(diffM)
    print(diffH)
    elapseH  = diffH 
    elapseM = diffM 
    
    if(diffH < 0 or (diffH == 0 and diffM < 0)): 
        elapseH = 23 + diffH 
        elapseM = 60 + diffM
        print("{}:{}".format(elapseH,elapseM))
    elif (diffM < 0): 
        elapseH = diffH - 1
        elapseM = 60 + diffM
        print("{}:{}".format(elapseH,elapseM))
    elif(diffH == 0 and diffM > 0):
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

# ***** START ALARM FUNCTION ***** 
if(args.controlMode == "alarm"):
    alarmH, alarmM = args.alarmTime.split(":")
    t1 = threading.Thread(target=alarmFunction, args=(alarmH, alarmM))
    t1.start()
    t1.join()
