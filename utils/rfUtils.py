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
rssi = -1000  # Global variable to store the latest RSSI value



def setupHackRF():
    global sdr, rxStream
    try:
        # 1. Connect to device
        devices = SoapySDR.Device.enumerate()
        if len(devices) == 0:
            print("ERROR: No HackRF found!")
            return False
        
        sdr = SoapySDR.Device(devices[0])
        
        # 2. Configure settings
        # Lowered sample rate to 2MHz (enough for RSSI, saves CPU/USB load)
        sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, 2e6) 
        sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, channels[0] * 1e6)
        sdr.setGain(SoapySDR.SOAPY_SDR_RX, 0, 30) # Slightly higher gain for detection
        
        # 3. Setup the stream (Allocates memory, but does not start it yet)
        rxStream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
        return True
    except Exception as e:
        print(f"Failed to setup SDR: {e}")
        return False

def closeHackRF():
    global sdr, rxStream
    if rxStream is not None:
        sdr.closeStream(rxStream)
    sdr = None

# Read RSSI value from HackRF (Cursed cause the HackRF is broken af)
def readRssi():
    global rssi, sdr, rxStream
    
    # Safety check
    if sdr is None:
        print("SDR not initialized, trying to reconnect...")
        setupHackRF()

    # 1. Start the flow of data
    sdr.activateStream(rxStream) 
    
    # Array to store accumulated power for averaging
    power_readings = []
    
    # Create a buffer (numpy array) for the samples
    buff = np.empty(1024, np.complex64) 

    try:
        # We read a few buffers to get a stable average
        for i in range(10): 
            sr = sdr.readStream(rxStream, [buff], len(buff))
            
            # Error checking on the read
            if sr.ret <= 0:
                continue # Skip bad reads
            
            # Slice the valid data
            valid_samples = buff[:sr.ret]
            
            # Calculate Power (I^2 + Q^2)
            # We use absolute squared to be faster: (real^2 + imag^2)
            power_val = np.mean(np.abs(valid_samples)**2)
            
            if power_val > 0:
                power_readings.append(power_val)
                
    except Exception as e:
        print(f"Read Error: {e}")

    finally:
        # 2. IMPORTANT: Stop the flow immediately to prevent buffer overflow/crash
        sdr.deactivateStream(rxStream)

    # Calculate final RSSI in dB
    if len(power_readings) > 0:
        avg_power = np.mean(power_readings)
        # 10*log10 because it is power. +1e-12 avoids log(0) error
        rssi_dbfs = 10.0 * math.log10(avg_power + 1e-12)
        rssi = rssi_dbfs # Update global

    return rssi

# Dont read just return latest reading
def getRssi():
    global rssi
    return rssi

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