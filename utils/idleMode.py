import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
from utils.config import *

# Idle mode routine for the drone

# Full scan pattern
def setIdleMode():
    rfUtils.scan()  # Initial scan at top position
    for i in range(90//18):
        motorUtils.movVertical(18, speedIdle)
        for j in range(360//18):
            rfUtils.scan()
            motorUtils.movHorizontal(18, speedIdle)
    motorUtils.resetPosition()
