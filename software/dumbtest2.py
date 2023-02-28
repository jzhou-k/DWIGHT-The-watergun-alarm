def enterCoord(): 
    while True:

        print("Enter x and y, enter 'q' to quit")
        x = input("Enter x: ")
        y = input("Enter y: ")
        if x == 'q' or y == 'q':
            break
        else:
            print(x,y)



#vs code shortcuts? 
enterCoord();
