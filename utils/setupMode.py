import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
import utils.idleMode as idleMode
from utils.config import *

# Setup routine for the Antidrone system
# OBS - Vertical movements are inverted due to gears
def setSetupMode():
    for i in range(3):  # Repeat the entire scanning process 3 times to get baseline noise levels
        rfUtils.scanBaseline()  # Initial scan at the top position
        for j in range(90//18):
            motorUtils.movVertical(18, speedSetup) # Move down by 18 degrees
            for k in range(360//18):
                rfUtils.scanBaseline()
                motorUtils.movHorizontal(18, speedSetup) # Move right by 18 degrees
        
        motorUtils.resetPosition() # Return to the top-position after each full scan
    