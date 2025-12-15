import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
from utils.config import *

# Idle mode routine for the drone

# Full scan pattern
def setIdleMode():
    for i in range(90//18):
        for j in range(360//18):
            rfUtils.scan()
            motorUtils.movHorizontal(18, speedIdle)
        motorUtils.movVertical(-18, speedIdle)
    rfUtils.scan()  # Final scan at the top position
    motorUtils.movVertical(90, speedIdle)
