# Integration between original facial detect ad open cv dnn facial detection


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

import pygame

from yunet import YuNet

# Initialize pygame
pygame.init()
quitEvent = threading.Event() 

X_CENTER = 200 
Y_CENTER = 150

#Huge accuracy issues ???????????????????????????????
# In cm
# idx 1 negative to the left 
# idx 2 negative down 
# hindsight this will work better as a object right... fuck 
# Configure so the gun defaults to aim at the center of the camera footage
# Turret will be the reference position, 
# idx = 0 x distance of camera, idx = 1 y distance of camera, 
# idx = 2 how far away the camera is, 
# idx = 3 - 4aspect ratio of camera footage x,y, 
# idx = 5-6 actual aim coord, default is centered, this will change
# pixel scale factor
# trigger 
# shoot
positionInfo = [-25,-30,75,400,300,X_CENTER,Y_CENTER,0.2,0,0] #1px = 1cm need to test this out with a ruler or something(a sheet of paper with notchings)

# Set up the joystick

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



def visualize(image, results, box_color=(0, 255, 0), text_color=(0, 0, 255), fps=None):
    output = image.copy()
    output = cv.cvtColor(output, cv.COLOR_BGR2RGB)
    landmark_color = [
        (255,   0,   0),  # right eye
        (0,   0, 255),  # left eye
        (0, 255,   0),  # nose tip
        (255,   0, 255),  # right mouth corner
        (0, 255, 255)  # left mouth corner
    ]

    if fps is not None:
        cv.putText(output, 'FPS: {:.2f}'.format(
            fps), (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, text_color)

    for det in (results if results is not None else []):
        bbox = det[0:4].astype(np.int32)
        cv.rectangle(output, (bbox[0], bbox[1]),
                     (bbox[0]+bbox[2], bbox[1]+bbox[3]), box_color, 2)
        
        #Prints the confidence 
        conf = det[-1]
        cv.putText(output, '{:.2f}'.format(
            conf), (bbox[0], bbox[1]+12), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)

        #Prints the center coord 
        centerx = bbox[2] / 2 + bbox[0]
        centery = bbox[3] / 2 + bbox[1]
        coord = (int(centerx), int(centery))
        cv.putText(output, 'Coord: {:.2f} , {:.2f}'.format(
            centerx, centery), (bbox[0], bbox[1]-12), cv.FONT_HERSHEY_DUPLEX, 0.4, box_color)
        cv.circle(output, coord, 1, box_color, 2)


        landmarks = det[4:14].astype(np.int32).reshape((5, 2))
        for idx, landmark in enumerate(landmarks):
            cv.circle(output, landmark, 2, landmark_color[idx], 2)

    return output, coord 



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
                    help='Usage: Set ???True??? to save file with results (i.e. bounding box, confidence level). Invalid in case of camera input. Default will be set to ???False???.')
parser.add_argument('--vis', '-v', type=str2bool, default=True,
                    help='Usage: Default will be set to ???True??? and will open a new window to show results. Set to ???False??? to stop visualizations from being shown. Invalid in case of camera input.')
# Used to control turret movment
parser.add_argument('--controlMode', type=str, default="noAlarm",
                    help='Usage: manual: Control coord with mouse click, alarm: alarmMode with face detection')
parser.add_argument('--alarmTime', type=str, default = "8:30",
                    help='Usage: will allow for user input for alarm time')
args = parser.parse_args()




#Alarm setting better way of setting alarm bruh 
def alarmFunction(h,m):
    
    def countTime(stop_event): 

        while not stop_event.is_set():
         
            timeNow = datetime.datetime.now().strftime("%H:%M:%S")
            
            #over at the arduino side, this will use different parser for Time 
            timeNow = timeNow + "T"
            print(timeNow)
            #writeData(timeNow)
            stop_event.wait(1)

    # Get the current time
    now = datetime.datetime.now()
    stop_event = threading.Event()


    #TO actually enter the alarm time e.g 7:30 
    #This is the most dumb solution :                                  ^) 
    #Parse string to hour min then pass into time delta, the day will be incremented automatically 
    # 'Wed Jun  9 04:26:40 1993'. standard format 
    alarmH = h
    alarmM = m
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

if(args.controlMode == "alarm"):
    alarmH, alarmM = args.alarmTime.split(":")
    t1 = threading.Thread(target=alarmFunction, args=(int(alarmH), int(alarmM)))
    t1.start()
    t1.join()


esp32 = serial.Serial('COM7',115200,timeout=.1)
def writeData(data):
    esp32.write(data.encode())
    #print(data)

#in its own thread 
def enterCoord(): 
    while True:
        print("Enter x and y, enter 'q' to quit")
        x = input("Enter x: ")
        y = input("Enter y: ")
        if x == 'q' or y == 'q':
            break
        else:
            x = int(x)
            y = int(y)
            moveNshoot(x,y,1)

def joystickMove(): 

    pygame.joystick.init()
    joystickList = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    joystick = joystickList[0]
    convert = (0.001)
    # Loop to get joystick events
    while True:
        t = 0 #python mainControl.py
        positionInfo[-2] = t
        for event in pygame.event.get():            
            if event.type == pygame.JOYBUTTONDOWN: 
                #exits the entire program (like a boss)
                if event.button == 6: 
                    pygame.quit()
                    quit() 
                elif event.button == 1: 
                    positionInfo[5] = X_CENTER
                    positionInfo[6] = Y_CENTER 
                elif event.button == 0: 
                    print("FIREEEEEEEE")
                    t = 1 
                    positionInfo[-2] = t 
                    time.sleep(0.5)
            
        
            elif event.type == pygame.JOYHATMOTION:
                # Get the button that was pressed
                if event.value == (0, 1):
                    print("D-pad up pressed")
                    positionInfo[6] += 10 
                elif event.value == (0, -1):
                    print("D-pad down pressed")
                    positionInfo[6] -= 10 
                elif event.value == (-1, 0):
                    print("D-pad left pressed")
                    positionInfo[5] -= 10 
                elif event.value == (1, 0):
                    print("D-pad right pressed")
                    positionInfo[5] += 10        
        

    
        # Get the axis values
        x_axis = joystick.get_axis(0)
        y_axis = joystick.get_axis(1)

        #Deadzone adjustment 
        if(x_axis <= 0.20 and x_axis >= -0.20): 
            x_axis = 0 
        if(y_axis <= 0.20 and y_axis >= -0.20): 
            y_axis = 0

        
        resultx = x_axis*(convert) + positionInfo[5]
        resulty = y_axis*(convert) + positionInfo[6]

        if(resultx < 0): 
            resultx = 0
        if(resulty < 0): 
            resulty = 0 
        
        positionInfo[5] = resultx
        positionInfo[6] = resulty
        

        # if( resultx >= 0 and resultx <= 420): 
        #     positionInfo[5] = resultx
        # if(resulty >= 0 and resulty <= 320): 
        #     positionInfo[6] = resulty
    #pygame.clock.tick(60) 

def getAngle(positionInfo):
    #Todo: You need to change the how it calculates the center >:c 
    scaleFactor = positionInfo[7]
    x = positionInfo[5]
    y = positionInfo[6]
    distance = positionInfo[2]
    #This is wrong, xangle is using 300/2 150 as center 
    #what the fuck is this code, god help me 
    xangle = 90 - math.degrees(math.atan((x*scaleFactor+positionInfo[0]-150*scaleFactor)/distance))
    yangle = 90 + math.degrees(math.atan((y*scaleFactor+positionInfo[1]-200*scaleFactor)/distance))
    return xangle, yangle


        

#x,y
#t is for trigger, enter 1 to shoot, 0 to not shoot 
#s is for sweep, it disregard x and y and sweeps according set values
def moveNshoot(x,y,t,s = 0): 
    positionInfo[5] = y
    positionInfo[6] = x 
    xangle,yangle = getAngle(positionInfo)
    data = "X{}Y{}Z{}S{}#".format(xangle,yangle,t,s)
    writeData(data)
    print(x,y)

def switchCoord(x,y): 
    #Transpose because camera is oriented differently
    temp = x 
    x = y 
    y = temp 
    return x,y

def moveNshootJoystick(): 
    xangle,yangle = getAngle(positionInfo)
    trigger = positionInfo[-2]
    shoot = positionInfo[-1]
    data = "X{}Y{}Z{}S{}#".format(xangle,yangle,trigger,shoot)
    writeData(data)
    #print(positionInfo[5],positionInfo[6])

def sendPos(): 
    while not quitEvent.is_set(): 
        time.sleep(0.3)
        print("{}, {}, {}, {}".format(round(positionInfo[5],1),round(positionInfo[6],1),positionInfo[-2],positionInfo[-1]))
        moveNshootJoystick()


def mainMode():
    mousePos = [200,200]
    #this function has to be nested or else it won't register the x,y coord 
    def mouseAction(action,x,y, *args): 
        if (action == cv.EVENT_RBUTTONDBLCLK or action == cv.EVENT_LBUTTONDBLCLK):
            moveNshoot(x,y,1)


        if(action==cv.EVENT_MOUSEMOVE): 
            #Not working because the new frames are over writing this text so, refer to visualize function
            mousePos[0] = x
            mousePos[1] = y
            #oh no
        
    path = 'results/'
    #enter coord in its thread 
    keyboard = threading.Thread(target=enterCoord)
    #Keeps tracks of joystick 
    joystickThreading = threading.Thread(target=joystickMove)
    #Continues to send angle data every 0.5 via serial communnication 
    sendPosThread = threading.Thread(target=sendPos)
    
    joystickThreading.start()
    sendPosThread.start() 
    #keyboard.start() 

    cv.namedWindow("Video", cv.WINDOW_NORMAL)
    cv.setMouseCallback("Video", mouseAction)

    detected = 0; #detected face 

    now = datetime.datetime.now()  
    startTime = time.time() 
    waitTime = 15 #waits for 120 seconds, if no face, start ?????? for 10 times (5 times from and back)
    elapsedTime = 0 
    sweep = True 

    while True:
        #print(args.controlMode)
        record = False 
        
        req = urllib.request.urlopen(
            'http://192.168.2.41/800x600.jpg')
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv.imdecode(arr, -1)  # 'Load it as it is'

        # Determine the where to crop
        height, width, channels = img.shape
        x, y, w, h = 0, 0, width//2, height//2  # example value

        # The model only detect max face size of 300 x 300
        crop_img = cv.resize(img, (400, 300),
                             interpolation=cv.INTER_LINEAR)
        image = cv.cvtColor(crop_img, cv.COLOR_RGB2BGR)
        image = cv.flip(image,0); #verticle flip to detect face upright 
        h, w, _ = image.shape


        cv.putText(image, 'Coord: {:.2f} , {:.2f}'.format(
            mousePos[0], mousePos[1]), (mousePos[0], mousePos[1]), cv.FONT_HERSHEY_DUPLEX, 0.3, (0,255,255))
        
        now = time.time()  
        ###################################SWEEEEP 
        elapsedTime =  now - startTime
        ###################################
        print(elapsedTime)
        # if less than waitTime, then keep checking for face, else sweep once, then back to detect face  
        if(elapsedTime < waitTime or not sweep): 
            positionInfo[-1] = 0 
            # Inference
            model.setInputSize([w, h])
            results = model.infer(image)
            #results != none doesnt work because results is a array hmm
            if(results is not None):
                print('{} faces detected.'.format(results.shape[0]))
                detected = detected + 1 
                
                record = True 
                for idx, det in enumerate(results):
                    print('{}: {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f}'.format(
                        idx, *det[:-1])
                    )

                # Draw results on the input image
                image, coord = visualize(image, results)
                #This will shoot everytime a face detected, might be a bad idea to code this....
                positionInfo[5], positionInfo[6] = switchCoord(coord[0]+20, coord[1])
                positionInfo[-2] = 1 

            elif(positionInfo[-2] == 1):
                time.sleep(0.5)
                positionInfo[-2] = 0
        


        else:
            sweep = False 
            record = True 
            positionInfo[-1] = 1 
            
        # Save results if save is true and record condition is met 
        if (args.save and record):
            print('Results saved to result{}.jpg\n'.format(detected))
            #lmao right its a file path 
            cv.imwrite(os.path.join(path, 'result{}.jpg'.format(detected)), image)

        # Visualize results in a new window
        if args.vis:
            cv.imshow("Video", image)
            key = cv.waitKey(5)  # delays for some seconds 0 delays for infinite times 
            if key == ord('q'):
                break
    

if __name__ == '__main__':
    # Instantiate YuNet
    model = YuNet(modelPath=args.model,
                  inputSize=[320, 320],
                  confThreshold=args.conf_threshold,
                  nmsThreshold=args.nms_threshold,
                  topK=args.top_k,
                  backendId=args.backend,
                  targetId=args.target)

    #Start main control mode 
    mainMode()
    #manualModeMouse()

cv.destroyAllWindows()
