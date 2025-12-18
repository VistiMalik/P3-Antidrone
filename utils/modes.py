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
def setupMode():
    global CURRENT_MODE
    CURRENT_MODE = 0
    rfUtils.setupHackRF()
    rfUtils.set_freq(channels[0])
    for i in range(setup_sweep_count):  # Repeat the entire scanning process 3 times to get baseline noise levels
        rfUtils.scanBaseline()  # Initial scan at the top position
        for row in range(90//9):
            motorUtils.movVertical(9, speedSetup) # Move down by 9 degrees
            for col in range(360//9):
                rfUtils.scanBaseline()
                motorUtils.movHorizontal(9, speedSetup) # Move right by 9 degrees

        motorUtils.resetPosition() # Return to the top-position after each full scan
        time.sleep(1)  # Short delay between opposite movements


# Idle mode routine for the drone
# Full scan pattern
def idleMode():
    global CURRENT_MODE
    CURRENT_MODE = 1

    rfUtils.rfCompBaseline()
    for row in range(90//18):
        motorUtils.movVertical(18, speedIdle) # Move down by 18 degrees
        for col in range(360//18):
            rfUtils.rfCompBaseline()  # Scan at current position
            motorUtils.movHorizontal(18, speedIdle) # Move right by 18 degrees
    
    motorUtils.resetPosition() # Return to the top-position after each full scan
    time.sleep(1)  # Short delay between opposite movements

    
def searchMode(from_jamming=False):
    global CURRENT_MODE
    CURRENT_MODE = 2
    threshold_reached_count = 0 # Count of consecutive RSSI readings above threshold

    # If comming from jamming mode we start in small increments of 9 degs
    if from_jamming:
        movement_scale = 9
    else:
        movement_scale = 18

    # If there's been an above-threshold reading in the last 10 seconds, keep searching
    while (time.time() - object_spotted_time) < 10:
        # Hill climb step on left and right 
        rssi_left = rfUtils.getRssiAndThreshold() # Read RSSI for left position
        motorUtils.movHorizontal(movement_scale, speedSearch) # Move to the right
        rssi_right = rfUtils.getRssiAndThreshold() # Read RSSI for right position
        if rssi_left > rssi_right:  # Compare right and left RSSI values
            motorUtils.movHorizontal(-movement_scale*2, speedSearch) # If left is stronger, move left twice, else just stay on new position


        # Hill climb step on up and down
        rssi_down = rfUtils.getRssiAndThreshold() # Read RSSI for down position
        motorUtils.movVertical(movement_scale, speedSearch) # Move up
        rssi_up = rfUtils.getRssiAndThreshold() # Read RSSI for up position
        if rssi_down > rssi_up: # Compare up and down RSSI values
            motorUtils.movVertical(-movement_scale*2, speedSearch) # If up is down is stroinger, move down twice, else just stay on new position  
        
        # If any of the readings exceed the threshold, increment the counter
        if rssi_left > rssi_threshold or rssi_right > rssi_threshold or rssi_up > rssi_threshold or rssi_down > rssi_threshold:
            threshold_reached_count += 1
            object_spotted_time = time.time()
        else: # If none of the readings exceed the threshold, reset the threshold counter
            threshold_reached_count = 0

        # Has there been 10 consecutive readings above the threshold then go to small mode if already in small mode start jamming
        if threshold_reached_count >= 10:
            if movement_scale == 9: # If in small mode
                pass # jamming_mode() # Start jamming
            else: 
                movement_scale = 9 # Go to small mode
                threshold_reached_count = 5 # Only needs 5 small mode readings to start jamming

        # Has 5 seconds passed since object was last spotted go back to normal search mode
        if (time.time() - object_spotted_time) > 5:
            movement_scale = 18 # Set mode to normal search mode
