import utils.motorUtils as motorUtils
import utils.rfUtils as rfUtils
import utils.setupMode as setupMode
# import utils.searchMode as searchMode
import utils.idleMode as idleMode

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

# Test idleMode
# while True:
#     idleMode.idleMode()
# exit()

# Test setupMode
while True:
    setupMode.setupMode()
    print("Completed one setupMode cycle")
exit()


