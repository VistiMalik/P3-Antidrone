import time
import utils.modes as modes
from utils.config import *
import utils.motorUtils as motorUtils
import random

# Global variable to keep track of the current scan section
baseline_avgs = {}   # Baseline averages for the 101 sections
# newbaseline_sums = [0.0] * 101  # New baseline sums for 101 sections
# newbaseline_avgs = []   # New baseline averages for the 101 sections


def readRssi():
    # Placeholder function to simulate updating RF values for a given section
    return random.randint(30, 70)  # Example RSSI value

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