import time
import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
from utils.config import *

CURRENT_MODE = "STARTING..."  # Global variable to track current mode

OBJ_SPOTTED_COORDS = {"horizontal": -1, "vertical": -1}  # Global variable to track spotted object coordinates
OBJ_SPOTTED_INIT_COORDS = {"horizontal": -1, "vertical": -1}  # Global variable to track initial spotted object coordinates
OBJ_SPOTTED_TIME = 0  # Timestamp of when the object was last spotted


def getCurrentMode():
    global CURRENT_MODE
    return CURRENT_MODE

# Setup routine for the Antidrone system
# OBS - Vertical movements are inverted due to gears
def setupMode():
    global CURRENT_MODE
    CURRENT_MODE = 0
    rfUtils.setupHackRF()
    time.sleep(0.5)
    rfUtils.set_freq(channels[0]*1e6)
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
    global OBJ_SPOTTED_TIME
    CURRENT_MODE = 2
    OBJ_SPOTTED_TIME = time.time()
    threshold_reached_count = 0 # Count of consecutive RSSI readings above threshold

    # If comming from jamming mode we start in small increments of 9 degs
    if from_jamming:
        movement_scale = 9
    else:
        movement_scale = 18

    # If there's been an above-threshold reading in the last 10 seconds, keep searching
    while (time.time() - OBJ_SPOTTED_TIME) < 10:
        for i in range(threshold_confirm_iterations):  # Perform 20 iterations of hill climbing
            # Hill climb step on left and right 
            rssi_left = rfUtils.getRssiSubBaseline() # Read RSSI for left position
            motorUtils.movHorizontal(movement_scale, speedSearch) # Move to the right
            rssi_right = rfUtils.getRssiSubBaseline() # Read RSSI for right position
            if rssi_left > rssi_right:  # Compare right and left RSSI values
                motorUtils.movHorizontal(-movement_scale*2, speedSearch) # If left is stronger, move left twice, else just stay on new position


            # Hill climb step on up and down
            rssi_down = rfUtils.getRssiSubBaseline() # Read RSSI for down position
            motorUtils.movVertical(movement_scale, speedSearch) # Move up
            rssi_up = rfUtils.getRssiSubBaseline() # Read RSSI for up position
            if rssi_down > rssi_up: # Compare up and down RSSI values
                motorUtils.movVertical(-movement_scale*2, speedSearch) # If up is down is stroinger, move down twice, else just stay on new position  
            
            # If any of the readings exceed the threshold, increment the counter
            if max(rssi_left, rssi_right, rssi_up, rssi_down) > rssi_threshold: #We only need to check if one reading exceeds the threshold, so we use max()
                threshold_reached_count += 1

        if threshold_reached_count / threshold_confirm_iterations >= threshold_breach_percentage:
            OBJ_SPOTTED_TIME = time.time()  # Update last spotted time

        # Has there been 10 consecutive readings above the threshold then go to small mode if already in small mode start jamming
        if threshold_reached_count / threshold_confirm_iterations >= go_small_mode_percentage:
            if movement_scale == 9: # If in small mode
                pass # jamming_mode() # Start jamming
            else: 
                movement_scale = 9 # Go to small mode
        threshold_reached_count = 0  # Reset counter for next iteration

        # Has 5 seconds passed since object was last spotted go back to normal search mode
        if (time.time() - OBJ_SPOTTED_TIME) > 5:
            movement_scale = 18 # Set mode to normal search mode

    motorUtils.resetPosition() # Return to the top-position after end of search
    time.sleep(1)  # Short delay between opposite movements
