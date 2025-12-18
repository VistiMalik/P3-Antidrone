import time
import random
import numpy as np
import math
from python_hackrf import pyhackrf  
import utils.modes as modes
from utils.config import *
import utils.motorUtils as motorUtils
import threading
import subprocess

# Global variable to keep track of the current scan section
baseline_avgs = {}   # Baseline averages for the 101 sections
rssi = -1000  # Global variable to store the latest RSSI value
rssi_lst = [-1000]*5
comp_value = 0  # Global variable to store the latest baseline subtracted value
sdr = None
rxStream = None


# -----------------------------
# Settings
# -----------------------------
sample_rate = 15e6
baseband_filter = 7.5e6
lna_gain = 30
vga_gain = 50

# -----------------------------
# Internal state
# -----------------------------
_sdr = None
_lock = threading.Lock()
_done = threading.Event()
_target = 0
_seen = 0
_power_sum = 0.0


def _rx_callback(device, buffer, buffer_length, valid_length):
    global _seen, _power_sum

    b = buffer[:valid_length].astype(np.int8)
    iq = b[0::2].astype(np.float32) + 1j * b[1::2].astype(np.float32)
    iq *= (1.0 / 128.0)

    with _lock:
        _power_sum += float(np.vdot(iq, iq).real)
        _seen += iq.size
        if _seen >= _target:
            _done.set()

    return 0

def setupHackRF():
    global _sdr
    pyhackrf.pyhackrf_init()
    _sdr = pyhackrf.pyhackrf_open()

    bw = pyhackrf.pyhackrf_compute_baseband_filter_bw_round_down_lt(baseband_filter)

    _sdr.pyhackrf_set_sample_rate(sample_rate)
    _sdr.pyhackrf_set_baseband_filter_bandwidth(bw)
    _sdr.pyhackrf_set_antenna_enable(False)
    _sdr.pyhackrf_set_amp_enable(False)
    _sdr.pyhackrf_set_lna_gain(lna_gain)
    _sdr.pyhackrf_set_vga_gain(vga_gain)

    _sdr.set_rx_callback(_rx_callback)

def closeHackRF():
    global _sdr
    if _sdr:
        try:
            _sdr.pyhackrf_stop_rx()
        except Exception:
            pass
        try:
            _sdr.pyhackrf_close()
        except Exception:
            pass
    pyhackrf.pyhackrf_exit()
    _sdr = None

def set_freq(freq_hz: float):
    _sdr.pyhackrf_set_freq(freq_hz)
    time.sleep(0.02)  

def readRssi(num_samples: int = 250_000) -> float | None:
    """
    Returns RSSI as wideband power in dBFS.
    """
    global _seen, _power_sum, _target, rssi, rssi_lst

    with _lock:
        _seen = 0
        _power_sum = 0.0
        _target = num_samples
    _done.clear()

    _sdr.pyhackrf_start_rx()
    ok = _done.wait(timeout=2.0)
    try:
        _sdr.pyhackrf_stop_rx()
    except Exception:
        pass

    if not ok:
        return None

    with _lock:
        if _seen == 0 or _power_sum <= 0:
            return None
        mean_power = _power_sum / _seen

    rssi = 10.0 * math.log10(mean_power + 1e-12)
    rssi_lst.append(rssi)
    rssi_lst.remove(rssi_lst[0])
    return rssi

# Dont read just return latest reading
def getRssi():
    global rssi_lst
    avg_rssi = sum(rssi_lst) / len(rssi_lst)
    return avg_rssi

# Don't calculate just return latest reading with baseline subtracted
def getCompValue():
    global comp_value
    return comp_value

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
    global comp_value
    coords = motorUtils.getCoordString() # Get coords to use as key in baseline dict
    rssi_value = readRssi() # Read rssi value
    comp_value = rssi_value - baseline_avgs[coords] # Subtract baseline current rssi
    return comp_value
    

# Compare current RSSI with baseline and decide if search mode should be activated
def rfCompBaseline(): 
    global comp_value
    thresh_breached_cnt = 0
    for i in range(threshold_confirm_iterations):  # Take 20 readings to confirm threshold breach
        comp_value = getRssiSubBaseline() # Get baseline subtracted rssi
        if comp_value > rssi_threshold: # If reading exceeds threshold
            thresh_breached_cnt += 1    # Increment counter
    if thresh_breached_cnt / threshold_confirm_iterations >= threshold_breach_percentage:  # If 70% readings exceed threshold
        print("Drone detected! Entering search mode.") 
        modes.searchMode()  # Enter search mode