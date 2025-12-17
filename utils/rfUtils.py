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
    global sdr, rxStream, max_rssi

    N = 4096
    buff = np.empty(N * 2, np.int16)
    result = []

    for freq in channels:
        sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, freq * 1e6)
        time.sleep(0.05)

        sr = sdr.readStream(rxStream, [buff], N, timeoutUs=200000)
        if sr.ret > 0:
            iq = buff[:sr.ret * 2].astype(np.float32)

            i = iq[0::2]
            q = iq[1::2]

            power = np.mean((i*i + q*q) / (32768.0 * 32768.0))
            if power > 0:
                result.append(10.0 * math.log10(power))

    max_rssi = max(result) if result else None
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