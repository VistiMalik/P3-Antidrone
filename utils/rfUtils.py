import time
import random
import numpy as np
import math
import SoapySDR
import utils.modes as modes
from utils.config import *
import utils.motorUtils as motorUtils
import threading
import subprocess

# Global variable to keep track of the current scan section
baseline_avgs = {}   # Baseline averages for the 101 sections
rssi = None  # Global variable to store the latest RSSI value



def readRssi():
    global rssi
    for i in range(50):
        result = subprocess.run(
        ["python3", "utils/hackRFInteraction.py"],
        capture_output=True,
        text=True)

        try:
            rssi = float(result.stdout.strip())
            return rssi
        except:
            pass



def getMaxRssi():
    global rssi
    return rssi
    

# Function to scan for every section and iterate through sections
def scanBaseline():
    global baseline_avgs
    coords = motorUtils.getCoordString()
    rssi = readRssi()

    if coords not in baseline_avgs:
        baseline_avgs[coords] = 0
    baseline_avgs[coords] += rssi / setup_sweep_count 


# Get RSSI value subtracted by baseline average for current position
def getRssiSubBaseline():
    global baseline_avgs
    coords = motorUtils.getCoordString()
    rssi_value = readRssi()  
    comp_value = rssi_value - baseline_avgs[coords]
    return comp_value
    

# Compare current RSSI with baseline and decide if search mode should be activated
def rfCompBaseline(): 
    comp_value = getRssiSubBaseline()
    if comp_value > rssi_threshold: 
        print("Drone detected! Entering search mode.") 
        modes.searchMode()