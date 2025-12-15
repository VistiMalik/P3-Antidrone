import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
import utils.idleMode as idleMode
from utils.config import *

# Setup routine for the Antidrone system
# OBS - Vertical movements are inverted due to gears
def setSetupMode():
    motorUtils.movVertical(90, speedIdle)  # We start from the top position
    for i in range(3):  # Repeat the entire scanning process 3 times to get baseline noise levels
        for j in range(90//18):
            for k in range(360//18):
                rfUtils.scanBaseline()
                motorUtils.movHorizontal(18, speedSetup)
            motorUtils.movVertical(-18, speedSetup)
        rfUtils.scanBaseline()  # Final scan at the top position
        motorUtils.movVertical(90, speedIdle)  # Reset vertical position
    idleMode.setIdleMode()  # Switch to idle mode after setup is complete
    