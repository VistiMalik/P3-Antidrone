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
    sdr.setSampleRate(SoapySDR.SOAPY_SDR_RX, 0, 20e6)
    sdr.setGain(SoapySDR.SOAPY_SDR_RX, 0, 30)

    rxStream = sdr.setupStream(SoapySDR.SOAPY_SDR_RX, SoapySDR.SOAPY_SDR_CF32)
    sdr.activateStream(rxStream)



def readRssi():
    global sdr, rxStream, max_rssi
    buff = np.empty(4096, np.complex64)
    result = []

    # Keep trying until we get at least one valid measurement per channel
    while not result:
        result = []
        for freq in channels:
            sdr.setFrequency(SoapySDR.SOAPY_SDR_RX, 0, freq * 1e6)

            # Let tuner settle a bit
            time.sleep(0.05)

            # Flush a couple buffers after retune
            for _ in range(2):
                sr = sdr.readStream(rxStream, [buff], len(buff))
                if sr.ret <= 0:
                    continue

            # Now take one "real" read
            sr = sdr.readStream(rxStream, [buff], len(buff))
            if sr.ret > 0:
                x = buff[:sr.ret]

                # Power estimate (mean-square magnitude)
                power = np.mean((x.real * x.real) + (x.imag * x.imag))

                # Avoid log(0)
                rssi = 10.0 * math.log10(power + 1e-12)
                result.append(rssi)

        time.sleep(0.2)

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