# DWIGHT-The-watergun-alarm


## TLDR; 

This is a automatic water gun alarm that shoots people in the face to wake them up.
it will use esp32 camera module and opencv dnn model to detect faces and aim the watergun with 2 axis servos. 


All functions: 
- alarm function, input wake up time using arg parser
- face detection using dnn models (insert github link here)
- manual mouse control with/without camera output

(obviously I have to add extra functions to make my life harder)

Restrictions: 
- cannot detect face if it's at a extreme angle, or if you are not facing the camera 
- less detections with low lighting, might need to add a spotlight 

Things I learned: 
- simple serial communication using esp32 and python 
- more solidwork skills (rizz++)
- computer vision with open cv 
- how to read documentation better 

More things to add: 
- joystick control 
- increase accuracy 
- finger commanding 
- mouth detection 
- display alarm time using a screen 


## Demo 
insert photos and videos here 

## Hardware 
### parts and equipments I used: 
- 3d printer 
- some m3 screws of various lengths
- 20kg servo * 2 
- mg995 servo * 1
- Freenove ESP32-WROVER CAM Board
- male to male and male to female jumper wires
- breadboard
- A 4*1.5 AA battery holder and battery 
- Oh right, and a small watergun I got from Canadian Tire

## Software/Firmware 

nothing much to say here, the code is pretty simple.

Some things to note: 
- I'm using conda to install all the libraries 
- make sure the baud rate is matching between your board and your computer 
- when you are setting up the servo, make sure set up the pwm rate according to your servos datasheet 
- the face detection library im using only detect max face dimension of 300 x 300, so make sure to shrink your video down 
- not sure why, but you do have to run the python from terminal like 

        python main.py 


This invention is the epitome of unnecessary and extra, but hey, I'm studying engineering, what else am I going to use my skills on  . 

