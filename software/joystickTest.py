import pygame

# Initialize pygame
pygame.init()

# Set up the joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Loop to get joystick events
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            # Get the axis values
            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            
            # Print the axis values
            print("X Axis: {}, Y Axis: {}".format(x_axis, y_axis))
        
        elif event.type == pygame.JOYBUTTONDOWN: 
            if event.button == 6: 
                pygame.quit()
                quit() 
            elif event.button == 0: 
                print("FIREEEEEEEE")

        elif event.type == pygame.JOYHATMOTION:
            # Get the button that was pressed
            if event.value == (0, 1):
                print("D-pad up pressed")
            elif event.value == (0, -1):
                print("D-pad down pressed")
            elif event.value == (-1, 0):
                print("D-pad left pressed")
                joystick.stop_rumble()
            elif event.value == (1, 0):
                print("D-pad right pressed")
                
