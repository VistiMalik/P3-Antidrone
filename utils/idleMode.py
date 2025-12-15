import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils

# Idle mode routine for the drone

# Full scan pattern
def idleMode():
    for i in range(90//18):
        motorUtils.movVertical(18, 0.00075)
        for j in range(360//18):
            rfUtils.scan()
            motorUtils.movHorizontal(18, 0.005)
    motorUtils.movVertical(-90, 0.00075)
