import SoapySDR
import numpy as np
import math

def readRssi():    
    global sdr, rxStream, rssi
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
    
    return rssi_dbfs


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

def main():
    setupHackRF()
    rssi = readRssi()
    print(rssi)
    closeHackRF()

if __name__ == "__main__":
    main()
