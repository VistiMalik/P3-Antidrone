import time
import random
import numpy as np
import math
import SoapySDR
import utils.modes as modes
from utils.config import *
import utils.motorUtils as motorUtils
import threading


# Global variable to keep track of the current scan section
baseline_avgs = {}   # Baseline averages for the 101 sections
sdr = None  # Global SDR object
rxStream = None  # Global RX stream object
rssi = None
sdr_lock = threading.Lock()


def setupHackRF():
    global sdr
    global rxStream
    devices = SoapySDR.Device.enumerate()
    sdr = SoapySDR.Device(devices[0])  # Assuming the first device is the HackRF
    sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, 10e6)
    sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, channels[0]*1e6)
    sdr.setGain(SoapySDR.SOAPY_SDR_RX, 0, 20)
    # Setup stream
    rxStream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    sdr.activateStream(rxStream)

def closeHackRF():
    global sdr, rxStream
    try:
        if rxStream is not None:
            sdr.deactivateStream(rxStream)
            sdr.closeStream(rxStream)
    except Exception:
        pass
    rxStream = None
    sdr = None


def readRssi():
    global sdr, rxStream, rssi
    setupHackRF()
    rssi_dbfs = None

    # Read samples
    buff = np.empty(4096, np.complex64)
    for _ in range(50):
        sr = sdr.readStream(rxStream, [buff], len(buff))
        if sr.ret <= 0:
            continue
        
        x = buff[:sr.ret]
        power = float(np.mean((x.real * x.real) + (x.imag * x.imag)))

        if not math.isfinite(power) or power <= 0.0:
            continue
    

        rssi_dbfs = 10.0 * math.log10(power + 1e-12)
        rssi = rssi_dbfs  # store globally
    

        print(power)
        print(f"Estimated RSSI: {rssi_dbfs:.2f} dBFS")
    closeHackRF()
    return rssi_dbfs


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