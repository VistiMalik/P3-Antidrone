import time
import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
from utils.config import *

#  Search Mode for the antidrone system
def setSearchMode():
    print("Setting Search Mode...")
    time.sleep(1)
    print("Search Mode activated.")
    for i in range(90//18):
        for j in range(360//18):
            # rfUtils.scan()   # Search algorithm to be implemented
            motorUtils.movHorizontal(18, speedSearch)
        motorUtils.movVertical(-18, speedSearch)
    time.sleep(0.05) # Stabilization time for vertical direction switch
    motorUtils.movVertical(90, speedSearch)
    time.sleep(1)
    print("No drone detected in the vicinity.")
    time.sleep(1)
    print("Going back to idle mode.")
    motorUtils.movVertical(-90, speedSearch)