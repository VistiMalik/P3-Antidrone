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
    rfUtils.scanBaseline()
    for i in range(setup_sweep_count):  # Repeat the entire scanning process 2 times to get baseline noise levels
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
    from_search_mode = False

    from_search_mode = rfUtils.rfCompBaseline()
    if from_search_mode:
        return
    for row in range(90//18):
        motorUtils.movVertical(18, speedIdle) # Move down by 18 degrees
        for col in range(360//18):
            from_search_mode = rfUtils.rfCompBaseline()  # Scan at current position
            if from_search_mode:
                return
            motorUtils.movHorizontal(18, speedIdle) # Move right by 18 degrees
    
    motorUtils.resetPosition() # Return to the top-position after each full scan
    time.sleep(1)  # Short delay between opposite movements

    
def searchMode():
    global CURRENT_MODE
    global OBJ_SPOTTED_TIME
    CURRENT_MODE = 2
    OBJ_SPOTTED_TIME = time.time()
    threshold_reached_count = 0 # Count of consecutive RSSI readings above threshold
    horz_optimum_found_count = 0 # Count of consecutive horizontal optimum readings found
    vert_optimum_found_count = 0 # Count of consecutive vertical optimum readings found
    last_horz_move = -1 # Last horizontal movement direction -- 0 means right, 1 means left, -1 means no movement yet
    last_vert_move = -1 # Last vertical movement direction -- 0 means up, 1 means down, -1 means no movement yet
    movement_scale = 18 # Initial movement scale for search mode

    # If there's been an above-threshold reading in the last 10 seconds, keep searching
    while (time.time() - OBJ_SPOTTED_TIME) < 10:
        for i in range(threshold_confirm_iterations):  # Perform 5 iterations of hill climbing
            # Hill climb step on left and right 
            rssi_left = rfUtils.avgGetRssiSubBaseline(5) # Read RSSI for left position
            print("Moving right")
            motorUtils.movHorizontal(movement_scale, speedSearch) # Move to the right
            
            rssi_right = rfUtils.avgGetRssiSubBaseline(5) # Read RSSI for right position
            print(f"right: {rssi_right}, left: {rssi_left}")
            if rssi_left > rssi_right:  # Compare right and left RSSI values
                print("Left is best")
                motorUtils.movHorizontal(-movement_scale*2, speedSearch) # If left is stronger, move left twice, else just stay on new position
                if last_horz_move == 0:  # If last move was to the right
                    horz_optimum_found_count += 1  # Increment optimum counter
                last_horz_move = 1  # Set last horizontal move to left
            else:
                if last_horz_move == 1:  # If last move was to the left
                    horz_optimum_found_count += 1  # Increment optimum counter
                last_horz_move = 0  # Set last horizontal move to right


            # Hill climb step on up and down
            rssi_down = rfUtils.avgGetRssiSubBaseline(5) # Read RSSI for down position
            print("Moving up")
            motorUtils.movVertical(movement_scale, speedSearch) # Move up
            rssi_up = rfUtils.avgGetRssiSubBaseline(5) # Read RSSI for up position
            print(f"right: {rssi_down}, left: {rssi_up}")
            if rssi_down > rssi_up: # Compare up and down RSSI values
                print("Down is best")
                motorUtils.movVertical(-movement_scale*2, speedSearch) # If up is down is stroinger, move down twice, else just stay on new position 
                if last_vert_move == 0:  # If last move was up
                    vert_optimum_found_count += 1  # Increment optimum counter
                last_vert_move = 1  # Set last vertical move to down
            else:
                if last_vert_move == 1:  # If last move was down
                    vert_optimum_found_count += 1  # Increment optimum counter
                last_vert_move = 0  # Set last vertical move to up 
            
            # If any of the readings exceed the threshold, increment the counter
            if max(rssi_left, rssi_right, rssi_up, rssi_down) > rssi_threshold: #We only need to check if one reading exceeds the threshold, so we use max()
                threshold_reached_count += 1

        if threshold_reached_count / threshold_confirm_iterations >= threshold_breach_percentage:
            OBJ_SPOTTED_TIME = time.time()  # Update last spotted time

        # Has there been 10 consecutive readings above the threshold then go to small mode if already in small mode start jamming
        if horz_optimum_found_count / threshold_confirm_iterations >= optimum_confirmed_percentage and vert_optimum_found_count / threshold_confirm_iterations >= optimum_confirmed_percentage:
            if movement_scale == 9: # If in small mode
                jammingMode() # Start jamming
                CURRENT_MODE = 2 # Return to search mode after jamming
            else: 
                movement_scale = 9 # Go to small mode
        threshold_reached_count = 0  # Reset counter for next iteration
        horz_optimum_found_count = 0  # Reset counter for next iteration
        vert_optimum_found_count = 0  # Reset counter for next iteration

        # Has 5 seconds passed since object was last spotted go back to normal search mode
        if (time.time() - OBJ_SPOTTED_TIME) > 5:
            movement_scale = 18 # Set mode to normal search mode

    motorUtils.resetPosition() # Return to the top-position after end of search
    time.sleep(1)  # Short delay between opposite movements

def jammingMode():
    global CURRENT_MODE
    CURRENT_MODE = 3
    print("Entering jamming mode")
    time.sleep(5)  # Simulate jamming duration
    print("Exiting jamming mode")
    time.sleep(1)  # Short delay before returning to other modes
