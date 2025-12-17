import time
import random
import numpy as np
import math
import SoapySDR
import utils.modes as modes
from utils.config import *
import utils.motorUtils as motorUtils


# Global variable to keep track of the current scan section
baseline_avgs = {}   # Baseline averages for the 101 sections
sdr = None  # Global SDR object
rxStream = None  # Global RX stream object
max_rssi = None


def setupHackRF():
    global sdr
    global rxStream
    devices = SoapySDR.Device.enumerate()
    sdr = SoapySDR.Device(devices[0])  # Assuming the first device is the HackRF
    sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, 10e6)
    sdr.setGain(SoapySDR.SOAPY_SDR_RX, 0, 30)

    rxStream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    sdr.activateStream(rxStream)

def readRssi():
    global sdr
    global rxStream
    global max_rssi
    buff = np.empty(4096, np.complex64)
    result = []
    while len(result) <= 0:
        for freq in channels:
            sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, freq * 1e6)
            time.sleep(0.05)  # allow tuner to settle
            
            sr = sdr.readStream(rxStream, [buff], len(buff), timeoutUs=int(200000))
            if sr.ret > 0:
                samples = buff[:sr.ret]
                power = np.mean(np.abs(samples)**2)
                rssi = 10 * math.log10(power)
                result.append(rssi)

    max_rssi = max(result)
    return result

def getMaxRssi():
    global max_rssi
    return max_rssi
    

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