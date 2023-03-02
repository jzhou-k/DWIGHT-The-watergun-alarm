from math import degrees
import threading
import time
import pygame

# Initialize pygame
pygame.init()
positionInfo = [-25,-30,75,400,300,200,150,0.2]
quitEvent = threading.Event()

def printPos(): 
    while not quitEvent.is_set(): 
        time.sleep(0.1)
        print("{}    {}".format(round(positionInfo[5],3),round(positionInfo[6],3)))


printPosThread = threading.Thread(target=printPos)
printPosThread.start() 



# Set up the joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Loop to get joystick events
while True:
    t = 0
    convert = 0.001
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            # exits the entire program (like a boss)
            if event.button == 6:
                quitEvent.set()
                pygame.quit()
                quit()
                
            elif event.button == 0:
                print("FIREEEEEEEE")
                t = 1

        # elif event.type == pygame.JOYAXISMOTION:
        #     # Get the axis values

        #         x_axis = joystick.get_axis(0)
        #         y_axis = joystick.get_axis(1)
        #         resultx = x_axis*(convert) + positionInfo[5]
        #         resulty = y_axis*(convert) + positionInfo[6]
            
        #         positionInfo[5] = resultx
        #         positionInfo[6] = y_axis 

        #         # if( resultx >= 0 and resultx <= 420): 
        #         #     positionInfo[5] = x_axis
        #         # if(resulty >= 0 and resulty <= 320): 
        #         #     positionInfo[6] = y_axis

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

    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)


    #Deadzone adjustment 
    if(x_axis <= 0.20 and x_axis >= -0.20): 
        x_axis = 0 
    if(y_axis <= 0.20 and y_axis >= -0.20): 
        y_axis = 0
    
    
    resultx = x_axis*(convert) + positionInfo[5]
    resulty = y_axis*(convert) + positionInfo[6]


    positionInfo[5] = resultx
    positionInfo[6] = resulty
