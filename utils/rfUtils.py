import time
import utils.modes as modes
from utils.config import *
import random

# Global variable to keep track of the current scan section
baseline_long = []
baseline_avgs = []   # Baseline averages for the 101 sections
baseline_len = 0
# newbaseline_sums = [0.0] * 101  # New baseline sums for 101 sections
# newbaseline_avgs = []   # New baseline averages for the 101 sections


def readRssi():
    # Placeholder function to simulate updating RF values for a given section
    return random.randint(30, 70)  # Example RSSI value

# Function to scan for every section and iterate through sections
def scanBaseline(round):
    global baseline_avgs
    global baseline_long
    global baseline_len

    if round == 1 and baseline_len == 0:
        baseline_len = len(baseline_long)
    
    baseline_long.append(readRssi())

    if len(baseline_long) == 3 * baseline_len:
        for reading in range(baseline_len):
            baseline_avgs.append((baseline_long[reading]+baseline_long[reading+baseline_len]+baseline_long[reading+2*baseline_len])/3)

def getRssiSubBaseline(section):#,rf_value):
    global baseline_avgs
    rssi_value = readRssi()  
    comp_value = rssi_value - baseline_avgs[section]
    return comp_value
    
def rfCompBaseline(section): 
    comp_value = getRssiSubBaseline(section)
    if comp_value > rssi_threshold: 
        print("Drone detected! Entering search mode.") 
        modes.setSearchMode()
        return True
    else:
        return False  # Example comparison