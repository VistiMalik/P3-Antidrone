import RPi.GPIO as GPIO
import time


PULL_H = 17 
PULL_V = 14
DIR_H = 27
DIR_V = 15
ENA_V = 26




def setup():
    GPIO.setmode(GPIO.BCM)  # Set mode to BCM

    # Set pinmodes (input/output pin?)
    GPIO.setup(PULL_H, GPIO.OUT)   
    GPIO.setup(DIR_H, GPIO.OUT)  
    GPIO.setup(PULL_V, GPIO.OUT)  
    GPIO.setup(DIR_V, GPIO.OUT)  
    GPIO.setup(ENA_V, GPIO.OUT)   


setup()
