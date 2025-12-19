import RPi.GPIO as GPIO
import time
from utils.config import *
import utils.motorUtils as motorUtils

# Constants:
STEP_ANGLE = 1.8
MICROSTEPS = 32
# Angle per microstep
ANGLE_PER_MICROSTEP = STEP_ANGLE / MICROSTEPS

# Pin defs imported from config.py
# Initial positions (defined in config.py):
coords = {"horizontal": horz_start_pos, "vertical": vert_start_pos}  # Initial coordinates

# Setup GPIO pins
def setup():
    GPIO.setmode(GPIO.BCM)  # Set mode to BCM

    # Set pinmodes (input/output pin?)
    GPIO.setup(PULL_H, GPIO.OUT, initial=GPIO.LOW)   
    GPIO.setup(DIR_H, GPIO.OUT, initial=GPIO.LOW)  
    GPIO.setup(PULL_V, GPIO.OUT, initial=GPIO.LOW)  
    GPIO.setup(DIR_V, GPIO.OUT, initial=GPIO.LOW)  



# Move stepper motor 1 (Horizontal)
def movHorizontal(degrees, speed=0.001):
    global coords

    steps_moved = 0

    raw_steps = degrees / ANGLE_PER_MICROSTEP * H_GEAR_RATIO # Adjust for gear ratio
    steps = abs(int(round(raw_steps, 0)))  # Convert degrees to steps (1 step = 1.8°) and remove sign

    # If move negative degrees turn on direction pin
    if degrees < 0: 
        direction = -1
        GPIO.output(DIR_H, GPIO.HIGH)
    else:
        direction = 1

    # Turn on and off pull pin step times, such it moves the steps
    for i in range(steps):
        GPIO.output(PULL_H, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(PULL_H, GPIO.LOW)
        time.sleep(speed)
        steps_moved += 1

        coords["horizontal"] += (ANGLE_PER_MICROSTEP / H_GEAR_RATIO) * direction
        coords["horizontal"] %= 360  
    direction = 1
    GPIO.output(DIR_H, GPIO.LOW) # Turn off/reset direction pin

# Move stepper motor 2 (Vertical)
def movVertical(degrees, speed=0.001):
    global coords

    ###### Trapezoidal profile can be implemented here for smoother movement ######

    # Check if move is within bounds (0-90 degrees)
    if coords["vertical"] + degrees > vert_max or coords["vertical"] + degrees < vert_min:
        print("Vertical movement out of bounds")
        return
    else:
        steps_moved = 0
        raw_steps = degrees / ANGLE_PER_MICROSTEP * V_GEAR_RATIO # Adjust for gear ratio
        steps = abs(int(round(raw_steps, 0)))  # Convert degrees to steps (1 step = 1.8°) and remove sign

        # If move negative degrees turn on direction pin
        if degrees < 0: 
            direction = -1
            GPIO.output(DIR_V, GPIO.HIGH)
        else:
            direction = 1

        # Turn on and off pull pin step times, such it moves the steps
        for i in range(steps):
            GPIO.output(PULL_V, GPIO.HIGH)
            time.sleep(speed)
            GPIO.output(PULL_V, GPIO.LOW)
            time.sleep(speed)
            steps_moved += 1
                
            coords["vertical"] += (ANGLE_PER_MICROSTEP / V_GEAR_RATIO) * direction
        direction = 1
            # coords["vertical"] %= 360  # It should not be necessary to wrap vertical position
        
        direction = 1
        GPIO.output(DIR_V, GPIO.LOW) # Turn off/reset direction pin

def getCoords():
    global coords
    return coords

def getCoordString(): 
    coords = motorUtils.getCoords()
    vert = str(round(coords["vertical"], 0) % 360).split(".")[0]
    horz = str(round(coords["horizontal"], 0) % 360).split(".")[0]
    coord_string = f"{vert}_{horz}"
    print(coord_string)
    if vert == "0":
        coord_string = "0_0"
    
    return coord_string

def resetPosition():
    delta_h_1 = 360 - coords["horizontal"] + horz_start_pos % 360
    delta_h_2 = -coords["horizontal"] + horz_start_pos
    delta_v = -coords["vertical"] + vert_start_pos

    if abs(delta_h_1) < abs(delta_h_2):
        delta_h = delta_h_1
    else:
        delta_h = delta_h_2
    
    movHorizontal(delta_h, speedIdle)
    movVertical(delta_v, speedIdle)

setup()
