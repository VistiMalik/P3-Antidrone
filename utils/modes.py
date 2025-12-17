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



def getCurrentMode():
    global CURRENT_MODE
    return CURRENT_MODE

# Setup routine for the Antidrone system
# OBS - Vertical movements are inverted due to gears
def setSetupMode():
    global CURRENT_MODE
    CURRENT_MODE = 0

    for i in range(3):  # Repeat the entire scanning process 3 times to get baseline noise levels
        rfUtils.scanBaseline(i)  # Initial scan at the top position
        for row in range(90//9):
            motorUtils.movVertical(9, speedSetup) # Move down by 9 degrees
            for col in range(360//9):
                rfUtils.scanBaseline(i)
                motorUtils.movHorizontal(9, speedSetup) # Move right by 9 degrees

        motorUtils.resetPosition() # Return to the top-position after each full scan
        time.sleep(1)  # Short delay between opposite movements


# Idle mode routine for the drone
# Full scan pattern
def setIdleMode():
    global CURRENT_MODE
    CURRENT_MODE = 1

    rfUtils.rfCompBaseline(0)
    for row in range(90//18):
        motorUtils.movVertical(18, speedIdle) # Move down by 18 degrees
        for col in range(360//18):
            rfUtils.rfCompBaseline(row*col+col+1)  # Scan at current position
            motorUtils.movHorizontal(18, speedIdle) # Move right by 18 degrees
    
    motorUtils.resetPosition() # Return to the top-position after each full scan
    time.sleep(1)  # Short delay between opposite movements

    

