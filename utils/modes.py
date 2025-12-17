import time
import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
from utils.config import *

CURRENT_MODE = "STARTING..."  # Global variable to track current mode

OBJ_SPOTTED_COORDS = {"horizontal": -1, "vertical": -1}  # Global variable to track spotted object coordinates
OBJ_SPOTTED_INIT_COORDS = {"horizontal": -1, "vertical": -1}  # Global variable to track initial spotted object coordinates
OBJ_SPOTTED = False  # Flag to indicate if an object has been spotted
OBJ_SPOTTED_TIME = 0  # Timestamp of when the object was spotted
OBJ_NO_LONGER_SPOTTED_TIME = 0  # Timestamp of when the object was no longer spotted

# Setup routine for the Antidrone system
# OBS - Vertical movements are inverted due to gears
def setSetupMode():
    global CURRENT_MODE
    CURRENT_MODE = 0

    for i in range(3):  # Repeat the entire scanning process 3 times to get baseline noise levels
        rfUtils.scanBaseline()  # Initial scan at the top position
        for j in range(90//18):
            motorUtils.movVertical(18, speedSetup) # Move down by 18 degrees
            for k in range(360//18):
                rfUtils.scanBaseline()
                motorUtils.movHorizontal(18, speedSetup) # Move right by 18 degrees
        
        motorUtils.resetPosition() # Return to the top-position after each full scan
        time.sleep(1)  # Short delay between opposite movements


# Idle mode routine for the drone

# Full scan pattern
def setIdleMode():
    global CURRENT_MODE
    CURRENT_MODE = 1

    rfUtils.scan()  # Initial scan at top position
    for i in range(90//18):
        motorUtils.movVertical(18, speedIdle)
        for j in range(360//18):
            rfUtils.scan()
            motorUtils.movHorizontal(18, speedIdle)
    motorUtils.resetPosition()
    time.sleep(1)  # Short delay between opposite movements


#  Search Mode for the antidrone system
def setSearchMode():
    global CURRENT_MODE
    global OBJ_SPOTTED_COORDS
    global OBJ_SPOTTED_INIT_COORDS
    global OBJ_SPOTTED_TIME
    global OBJ_NO_LONGER_SPOTTED_TIME
    CURRENT_MODE = 2

    OBJ_SPOTTED = True
    OBJ_SPOTTED_INIT_COORDS = motorUtils.getCoords()
    OBJ_SPOTTED_COORDS = motorUtils.getCoords()
    OBJ_SPOTTED_TIME = time.time() # Timestamp of when the object was spotted (Maybe use to stop algo)

    # IMPLEMENT SEARCH ALGORITHM HERE #
    while time.time() - OBJ_SPOTTED_TIME < 10:  # Search mode runs for 10 seconds after spotting an object
        if evalNeighborCoords():    # If a better coordinate is found,
            moveToNext()            # Move to the next coordinate
        else:
            print("local maximum found!")
        rfUtils.scan()  # Scan at current position

    # Test movements in search mode
    # print("Setting Search Mode...")
    # time.sleep(1)
    # print("Search Mode activated.")
    # for i in range(90//18):
    #     motorUtils.movVertical(18, speedSearch)
    #     for j in range(360//18):
    #         # rfUtils.scan()   # Search algorithm to be implemented
    #         motorUtils.movHorizontal(18, speedSearch)
    # time.sleep(0.05) # Stabilization time for vertical direction switch
    # time.sleep(1)
    # print("No drone detected in the vicinity.")

    OBJ_SPOTTED = False
    OBJ_NO_LONGER_SPOTTED_TIME = time.time()

    time.sleep(1)
    print("Going back to idle mode.")
    motorUtils.resetPosition()
    time.sleep(1)  # Short delay between opposite movements

def getCurrentMode():
    global CURRENT_MODE
    return CURRENT_MODE

def evalNeighborCoords():
    should_move = False
    # Placeholder function to evaluate neighboring coordinates
    print("Evaluating neighboring coordinates for better drone signal...")
    # Actual implementation would go here

    return should_move

def moveToNext():
    # Placeholder function to move to the next coordinate
    print("Moving to the next coordinate...")
    # Actual implementation would go here
