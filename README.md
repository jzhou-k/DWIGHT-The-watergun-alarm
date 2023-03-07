# DWIGHT-The-watergun-alarm

## TLDR

This is a automatic water gun alarm that shoots people in the face to wake them up. [^1]
it will use esp32 camera module and opencv dnn model to detect faces and aim the watergun with 2 axis servos.

All functions:

- alarm function, input wake up time using arg parser
- face detection using YUNET dnn models [YUNET DNN model](https://github.com/jzhou-k/opencv_zoo/tree/master/models/face_detection_yunet)
- manual mouse control with/without camera output
- joystick control

(obviously I have to add extra functions to make my life harder)

Restrictions:

- cannot detect face if it's at a extreme angle, or if you are not facing the camera
- less detections with low lighting, might need to add a spotlight

More things to add:
- switch to raspberry pi 
- spotlight
- finger commanding
- mouth detection
- display alarm time using a screen (my oled screen is broken :    ^) )

## Demo

insert photos and videos here

## Hardware

### parts and equipments I used

- 3d printer, [The 3d parts](https://github.com/jzhou-k/DWIGHT-The-watergun-alarm/blob/main/hardware)
- some m3 screws of various lengths
- 20kg servo * 2
- mg995 servo * 1
- Freenove ESP32-WROVER CAM Board
- male to male and male to female jumper wires
- breadboard
- A 4*1.5 AA battery holder and battery
- Oh right, and a small watergun I got from Canadian Tire

### 3D parts 
![camera holder](https://github.com/jzhou-k/DWIGHT-The-watergun-alarm/blob/main/hardware/esp%20camera%20holder/image.png)
![camera holder backside](https://github.com/jzhou-k/DWIGHT-The-watergun-alarm/blob/main/hardware/esp%20camera%20holder/image%20back.png)
![gun mount](https://github.com/jzhou-k/DWIGHT-The-watergun-alarm/blob/main/hardware/gun%20mount.png)
![gunbrace attachment side](https://github.com/jzhou-k/DWIGHT-The-watergun-alarm/blob/main/hardware/brace%20attachment%20side.png)
![gunbrace trigger side](https://github.com/jzhou-k/DWIGHT-The-watergun-alarm/blob/main/hardware/gun%20brace%20and%20trigger%20servo%20holder.png)

## Software/Firmware

nothing much to say here, the code is pretty simple.

wifiCam.ino runs on esp32, it handles the camera server and parses strings to move the servos. 

mainControl.py contains the alarm function, once alarm rings it starts face detection and sends the string to esp32. 

Some things to note:

- I'm using conda to install all the libraries
- make sure the baud rate is matching between your board and your computer
- when you are setting up the servo, make sure set up the pwm rate according to your servos datasheet
- the face detection library im using only detect max face dimension of 300 x 300, so make sure to shrink your video down


[^1]: This invention is the epitome of unnecessary and extra, but hey, I'm studying engineering, what else am I going to use my skills on.
