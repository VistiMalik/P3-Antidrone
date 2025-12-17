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



# Read RSSI value from HackRF (Cursed cause the HackRF is broken af)
def readRssi():
    global rssi
    for i in range(50): # Try up to 50 times, such we can get errors and still continue with correct values
        # Spawn new python process to read RSSI with frequencies as arguments
        result = subprocess.run(
        ["python3", "utils/hackRFInteraction.py", f"{channels[0]}"],
        capture_output=True,
        text=True)

        # Try to convert output to float and return if it doesnt work wait and try to get result again
        try:
            rssi = float(result.stdout.strip())
            print("Hiii")
            return rssi
        except Exception as e:
            print(e)
            time.sleep(0.2)
    

# Function to scan for every section and iterate through sections
def scanBaseline():
    global baseline_avgs
    coords = motorUtils.getCoordString() # Get coords to use as key in baseline dict
    rssi = readRssi() # Read rssi value

    if coords not in baseline_avgs: # If coord entry not in baseline create it 
        baseline_avgs[coords] = 0
    baseline_avgs[coords] += rssi / setup_sweep_count # Add value to the baseline map 


# Get RSSI value subtracted by baseline average for current position
def getRssiSubBaseline():
    global baseline_avgs
    coords = motorUtils.getCoordString() # Get coords to use as key in baseline dict
    rssi_value = readRssi() # Read rssi value
    comp_value = rssi_value - baseline_avgs[coords] # Subtract baseline current rssi
    return comp_value
    

# Compare current RSSI with baseline and decide if search mode should be activated
def rfCompBaseline(): 
    comp_value = getRssiSubBaseline() # Get baseline subtracted rssi
    if comp_value > rssi_threshold: # Enter search mode if above threshold
        print("Drone detected! Entering search mode.") 
        modes.searchMode()  # Enter search mode