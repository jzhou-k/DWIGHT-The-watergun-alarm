import math 

def getAngle(positionInfo):
    #Todo: You need to change the how it calculates the center >:c 
    scaleFactor = positionInfo[7]
    #This is wrong, xangle is using 300/2 150 as center 
    xangle = 90 - math.degrees(math.atan((positionInfo[5]*scaleFactor+positionInfo[0]-150*scaleFactor)/positionInfo[2]))
    yangle = 90 + math.degrees(math.atan((positionInfo[6]*scaleFactor+positionInfo[1]-200*scaleFactor)/positionInfo[2]))
    return xangle, yangle

positionInfo = [-25,-25,75,400,300,150,250,0.2]
xangle, yangle = getAngle(positionInfo)
print("x{}y{}".format(xangle,yangle))
#115 
#105
#80

import numpy as np
import cv2 as cv
# mouse callback function


def function(): 
    def draw_circle(event,x,y,flags,param):
        if event == cv.EVENT_LBUTTONDBLCLK:
            #cv.circle(img,(x,y),100,(255,0,0),-1)
            cv.putText(img, 'Coord: {:.2f} , {:.2f}'.format(
            x, y), (x, y), cv.FONT_HERSHEY_DUPLEX, 0.3, (255,0,0))
    # Create a black image, a window and bind the function to window
    img = np.zeros((512,512,3), np.uint8)
    cv.namedWindow('image')
    cv.setMouseCallback('image',draw_circle)
    while(1):
        cv.imshow('image',img)
        if cv.waitKey(20) & 0xFF == 27:
            break

function()
cv.destroyAllWindows()