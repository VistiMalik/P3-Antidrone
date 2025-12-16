import RPi.GPIO as GPIO
import time
from utils.config import *

# Pin defs imported from config.py
# Initial positions (defined in config.py):
coords = {"horizontal": horz_start_pos, "vertical": vert_start_pos}  # Initial coordinates

# Setup GPIO pins
def setup():
    GPIO.setmode(GPIO.BCM)  # Set mode to BCM

    # Set pinmodes (input/output pin?)
    GPIO.setup(PULL_H, GPIO.OUT)   
    GPIO.setup(DIR_H, GPIO.OUT)  
    GPIO.setup(PULL_V, GPIO.OUT)  
    GPIO.setup(DIR_V, GPIO.OUT)  



# Move stepper motor 1 (Horizontal)
def movHorizontal(degrees, speed):
    global coords
    steps = abs(int(round(degrees/1.8, 0))) # Convert degrees to steps (1 step = 1.8°) and remove sign

    # If move negative degrees turn on direction pin
    if degrees < 0: 
        direction = -1
        GPIO.output(DIR_H, GPIO.HIGH)

    # Turn on and off pull pin step times, such it moves the steps
    for i in range(steps):
        GPIO.output(PULL_H, GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(PULL_H, GPIO.LOW)
        time.sleep(speed)
        coords["horizontal"] += ((1.8/32)*direction)%360

    direction = 1
    GPIO.output(DIR_H, GPIO.LOW) # Turn off/reset direction pin

# Move stepper motor 2 (Vertical)
def movVertical(degrees, speed):
    global coords

    # Check if move is within bounds (0-90 degrees)
    if coords["vertical"] + degrees > vert_max or coords["vertical"] + degrees < vert_min:
        print("Vertical movement out of bounds")
        return
    else:
        steps = abs(int(round(degrees/1.8, 0)))*3*32 # Convert degrees to steps (1 step = 1.8°) and remove sign and multiply by 3 due to gear ratio

        # If move negative degrees turn on direction pin
        if degrees < 0: 
            direction = -1
            GPIO.output(DIR_V, GPIO.HIGH)

        # Turn on and off pull pin step times, such it moves the steps
        for i in range(steps):
            GPIO.output(PULL_V, GPIO.HIGH)
            time.sleep(speed)
            GPIO.output(PULL_V, GPIO.LOW)
            time.sleep(speed)
            coords["vertical"] += ((1.8/32)*direction)%360

        direction = 1
        GPIO.output(DIR_V, GPIO.LOW) # Turn off/reset direction pin

def resetPosition():
    global coords
    movHorizontal(-coords["horizontal"] + horz_start_pos, speedIdle)
    movVertical(-coords["vertical"] + vert_start_pos, speedIdle)


def getCoords():
    global coords
    return coords

setup()