#Integration between original facial detect ad open cv dnn facial detection 


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

from yunet import YuNet

def str2bool(v):
    if v.lower() in ['on', 'yes', 'true', 'y', 't']:
        return True
    elif v.lower() in ['off', 'no', 'false', 'n', 'f']:
        return False
    else:
        raise NotImplementedError


#esp32 = serial.Serial('COM6',115200,timeout=.1)

backends = [cv.dnn.DNN_BACKEND_OPENCV, cv.dnn.DNN_BACKEND_CUDA]
targets = [cv.dnn.DNN_TARGET_CPU, cv.dnn.DNN_TARGET_CUDA, cv.dnn.DNN_TARGET_CUDA_FP16]
help_msg_backends = "Choose one of the computation backends: {:d}: OpenCV implementation (default); {:d}: CUDA"
help_msg_targets = "Choose one of the target computation devices: {:d}: CPU (default); {:d}: CUDA; {:d}: CUDA fp16"
try:
    backends += [cv.dnn.DNN_BACKEND_TIMVX]
    targets += [cv.dnn.DNN_TARGET_NPU]
    help_msg_backends += "; {:d}: TIMVX"
    help_msg_targets += "; {:d}: NPU"
except:
    print('This version of OpenCV does not support TIM-VX and NPU. Visit https://github.com/opencv/opencv/wiki/TIM-VX-Backend-For-Running-OpenCV-On-NPU for more information.')

parser = argparse.ArgumentParser(description='YuNet: A Fast and Accurate CNN-based Face Detector (https://github.com/ShiqiYu/libfacedetection).')
parser.add_argument('--input', '-i', type=str, help='Usage: Set input to a certain image, omit if using camera.')
parser.add_argument('--model', '-m', type=str, default='face_detection_yunet_2022mar.onnx', help="Usage: Set model type, defaults to 'face_detection_yunet_2022mar.onnx'.")
parser.add_argument('--backend', '-b', type=int, default=backends[0], help=help_msg_backends.format(*backends))
parser.add_argument('--target', '-t', type=int, default=targets[0], help=help_msg_targets.format(*targets))
parser.add_argument('--conf_threshold', type=float, default=0.9, help='Usage: Set the minimum needed confidence for the model to identify a face, defauts to 0.9. Smaller values may result in faster detection, but will limit accuracy. Filter out faces of confidence < conf_threshold.')
parser.add_argument('--nms_threshold', type=float, default=0.3, help='Usage: Suppress bounding boxes of iou >= nms_threshold. Default = 0.3.')
parser.add_argument('--top_k', type=int, default=5000, help='Usage: Keep top_k bounding boxes before NMS.')
parser.add_argument('--save', '-s', type=str, default=False, help='Usage: Set “True” to save file with results (i.e. bounding box, confidence level). Invalid in case of camera input. Default will be set to “False”.')
parser.add_argument('--vis', '-v', type=str2bool, default=True, help='Usage: Default will be set to “True” and will open a new window to show results. Set to “False” to stop visualizations from being shown. Invalid in case of camera input.')
args = parser.parse_args()

def visualize(image, results, box_color=(0, 255, 0), text_color=(0, 0, 255), fps=None):
    output = image.copy()
    output = cv.cvtColor(output, cv.COLOR_BGR2RGB)
    landmark_color = [
        (255,   0,   0), # right eye
        (  0,   0, 255), # left eye
        (  0, 255,   0), # nose tip
        (255,   0, 255), # right mouth corner
        (  0, 255, 255)  # left mouth corner
    ]

    if fps is not None:
        cv.putText(output, 'FPS: {:.2f}'.format(fps), (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, text_color)

    for det in (results if results is not None else []):
        bbox = det[0:4].astype(np.int32)
        cv.rectangle(output, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), box_color, 2)

        conf = det[-1]
        cv.putText(output, '{:.4f}'.format(conf), (bbox[0], bbox[1]+12), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)

        landmarks = det[4:14].astype(np.int32).reshape((5,2))
        for idx, landmark in enumerate(landmarks):
            cv.circle(output, landmark, 2, landmark_color[idx], 2)

    return output

if __name__ == '__main__':
    # Instantiate YuNet
    model = YuNet(modelPath=args.model,
                  inputSize=[320, 320],
                  confThreshold=args.conf_threshold,
                  nmsThreshold=args.nms_threshold,
                  topK=args.top_k,
                  backendId=args.backend,
                  targetId=args.target)

    while True: 
        # If input is an image
        if args.input is not None:

            req = urllib.request.urlopen('http://t2.gstatic.com/licensed-image?q=tbn:ANd9GcQ2wPmYNixF92zIj_LsxSjjJQ7vO3CdccFkVEdKIvofULXBOwzb-Ef1bYv11mkcW5SJ')
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv.imdecode(arr, -1) # 'Load it as it is'
            # Determine the ROI to crop
            
            height, width, channels = img.shape 
            x, y, w, h = 0, 0, width, int(height/2) # example values

            crop_img = img[y:y+h, x:x+w]
            crop_img = cv.resize(img, (300,300))

            #image = cv.imread('side.jpg')
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
                cv.namedWindow("Video", cv.WINDOW_AUTOSIZE)
                cv.imshow("Video", image)
                key = cv.waitKey(0) #delays for some seconds 
                if key==ord('q'):
                     break
        else: # Omit input to call default camera
            deviceId = 0
            cap = cv.VideoCapture(deviceId)
            w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            model.setInputSize([w, h])

            tm = cv.TickMeter()
            while cv.waitKey(1) < 0:
                hasFrame, frame = cap.read()
                if not hasFrame:
                    print('No frames grabbed!')
                    break

                # Inference
                tm.start()
                results = model.infer(frame) # results is a tuple
                tm.stop()

                # Draw results on the input image
                frame = visualize(frame, results, fps=tm.getFPS())

                # Visualize results in a new Window
                cv.imshow('YuNet Demo', frame)

                tm.reset()

cv.destroyAllWindows()