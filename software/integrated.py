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

import numpy as np
import cv2 as cv

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt 
from PyQt5.QtWidgets import QDesktopWidget

from yunet import YuNet

esp32 = serial.Serial('COM6',115200,timeout=.1)
def writeData(data):
    esp32.write(data.encode())
    print(data)


dim = (400, 300)
# In cm
# hindsight this will work better as a object right... fuck 
# Configure so the gun defaults to aim at the center of the camera footage
# Turret will be the reference position, 
# idx = 0 x distance of camera, idx = 1 y distance of camera, 
# idx = 2 how far away the camera is, 
# idx = 3 - 4aspect ratio of camera footage x,y, 
# idx = 5-6 actual aim coord default is centered, this will change
# pixel scale factor
positionInfo = [8,8,75,400,300,200,150,0.2] #1px = 1cm 

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(dim[0], dim[1])

    def mousePressEvent(self, event):
        #print("Mouse clicked at", event.x(), event.y())
        self.handle_mouse_click(event.x(), event.y())

    def handle_mouse_click(self, x, y):
        positionInfo[5] = x
        positionInfo[6] = y 
        xangle,yangle = getAngle(positionInfo)
        t = 0
        data = "X{}Y{}T{}#".format(xangle,yangle,t)
        writeData(data)
        # print(data)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
    
    def center(self):
        # Get the dimensions of the screen
        screen = QDesktopWidget().screenGeometry()

        # Calculate the position of the window
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2

        # Move the window to the center of the screen
        self.move(x, y)


def getAngle(positionInfo):
    #Todo: You need to change the how it calculates the center >:c 
    scaleFactor = positionInfo[7]
    xangle = 90 + math.degrees(math.atan((positionInfo[5]*scaleFactor+positionInfo[0]-200*scaleFactor)/positionInfo[2]))
    yangle = 90 + math.degrees(math.atan((positionInfo[6]*scaleFactor+positionInfo[1]-150*scaleFactor)/positionInfo[2]))
    return xangle, yangle


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
parser.add_argument('--save', '-s', type=str, default=False,
                    help='Usage: Set “True” to save file with results (i.e. bounding box, confidence level). Invalid in case of camera input. Default will be set to “False”.')
parser.add_argument('--vis', '-v', type=str2bool, default=True,
                    help='Usage: Default will be set to “True” and will open a new window to show results. Set to “False” to stop visualizations from being shown. Invalid in case of camera input.')
# Used to control turret movment
parser.add_argument('--controlMode', type=str, default="manual",
                    help='Usage: Control coord with mouse click')
parser.add_argument('--isAlarm', type=str2bool,default=False,
                    help='Usage: will allow for user input for alarm time')
args = parser.parse_args()


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

        conf = det[-1]
        cv.putText(output, '{:.2f}'.format(
            conf), (bbox[0], bbox[1]+12), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)
        centerx = bbox[2] / 2 + bbox[0]
        centery = bbox[3] / 2 + bbox[1]
        coord = (int(centerx), int(centery))
        cv.putText(output, 'Coord: {:.2f} , {:.2f}'.format(
            centerx, centery), (bbox[0], bbox[1]-12), cv.FONT_HERSHEY_DUPLEX, 0.4, box_color)
        cv.circle(output, coord, 1, box_color, 2)

        landmarks = det[4:14].astype(np.int32).reshape((5, 2))
        for idx, landmark in enumerate(landmarks):
            cv.circle(output, landmark, 2, landmark_color[idx], 2)

    return output


def cameraMode():
    while True:
        print(args.controlMode)
        req = urllib.request.urlopen(
            'http://t2.gstatic.com/licensed-image?q=tbn:ANd9GcQ2wPmYNixF92zIj_LsxSjjJQ7vO3CdccFkVEdKIvofULXBOwzb-Ef1bYv11mkcW5SJ')
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv.imdecode(arr, -1)  # 'Load it as it is'

        # Determine the where to crop
        height, width, channels = img.shape
        x, y, w, h = 0, 0, width, int(height/2)  # example values
        # fx = 0.5. fy = 0.5 resizes by half

        crop_img = img[y:1024, x:x+w]
        # The model only detect max face size of 300 x 300
        crop_img = cv.resize(crop_img, (400, 300),
                             interpolation=cv.INTER_LINEAR)
        image = cv.cvtColor(crop_img, cv.COLOR_RGB2BGR)
        h, w, _ = image.shape

        # Inference
        model.setInputSize([w, h])
        results = model.infer(image)

        # Print results
        print('{} faces detected.'.format(results.shape[0]))
        for idx, det in enumerate(results):
            print('{}: {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f} {:.0f}'.format(
                idx, *det[:-1])
            )

        # Draw results on the input image
        image = visualize(image, results)

        # Save results if save is true
        if args.save:
            print('Results saved to result.jpg\n')
            cv.imwrite('result.jpg', image)

        # Visualize results in a new window
        if args.vis:
            cv.namedWindow("Video", cv.WINDOW_NORMAL)
            cv.imshow("Video", image)
            key = cv.waitKey(1)  # delays for some seconds
            if key == ord('q'):
                break


def manualModeMouse():
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()

    # register mouse click at delay(0) so it just waits for it
    # display mouse click coord
    # display angle


if __name__ == '__main__':
    # Instantiate YuNet
    model = YuNet(modelPath=args.model,
                  inputSize=[320, 320],
                  confThreshold=args.conf_threshold,
                  nmsThreshold=args.nms_threshold,
                  topK=args.top_k,
                  backendId=args.backend,
                  targetId=args.target)

    #cameraMode()
    manualModeMouse()

cv.destroyAllWindows()
