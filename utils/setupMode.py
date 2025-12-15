import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils

# Setup routine for the Antidrone system
def setupMode():
    for i in range(3):  # Repeat the entire scanning process 3 times to get baseline noise levels
        for j in range(90//18):
            motorUtils.movVertical(18, 0.00075)
            for k in range(360//18):
                rfUtils.scanBaseline()
                motorUtils.movHorizontal(18, 0.005)


        motorUtils.movVertical(-90, 0.00075)  # Reset vertical position