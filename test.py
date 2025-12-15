import utils.motorUtils as motorUtils
import utils.setupMode as setupMode
import utils.idleMode as idleMode
import utils.rfUtils as rfUtils
from utils.config import *
import time


# Test vertical movement
# while True: 
#     motorUtils.movVertical(90, 0.001)
#     motorUtils.movVertical(-90, 0.03)
# exit()

# Test horizontal movement
# while True:
#     motorUtils.movHorizontal(90, 0.01)
#     motorUtils.movHorizontal(-90, 0.03)
# exit()

# Test setIdleMode
# while True:
# global rssi_threshold
#     idleMode.idleMode(rssi_threshold)
# exit()

# Test setupMode
while True:
    setupMode.setSetupMode()
    print("Completed one setupMode cycle")
exit()