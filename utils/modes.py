import time
import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
from utils.config import *

CURRENT_MODE = "STARTING..."  # Global variable to track current mode

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
        time.sleep(0.5)  # Short delay between opposite movements


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
    time.sleep(0.5)  # Short delay between opposite movements


#  Search Mode for the antidrone system
def setSearchMode():
    global CURRENT_MODE
    CURRENT_MODE = 2

    # IMPLEMENT SEARCH ALGORITHM HERE #

    print("Setting Search Mode...")
    time.sleep(1)
    print("Search Mode activated.")
    for i in range(90//18):
        motorUtils.movVertical(18, speedSearch)
        for j in range(360//18):
            # rfUtils.scan()   # Search algorithm to be implemented
            motorUtils.movHorizontal(18, speedSearch)
    time.sleep(0.05) # Stabilization time for vertical direction switch
    time.sleep(1)
    print("No drone detected in the vicinity.")
    time.sleep(1)
    print("Going back to idle mode.")
    motorUtils.resetPosition()
    time.sleep(0.5)  # Short delay between opposite movements

def getCurrentMode():
    global CURRENT_MODE
    return CURRENT_MODE
