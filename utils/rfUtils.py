import time
import utils.searchMode as searchMode
import utils.setupMode as setupMode
from utils.config import *

# Global variable to keep track of the current scan section
scan_section = 0
iteration_baseline = 0
iteration = 0
baseline_sums = [0.0] * 101  # Baseline sums for 101 sections
baseline_avgs = []   # Baseline averages for the 101 sections
# newbaseline_sums = [0.0] * 101  # New baseline sums for 101 sections
# newbaseline_avgs = []   # New baseline averages for the 101 sections

# Function to scan for every section and iterate through sections
def scanBaseline():
    global scan_section
    global iteration_baseline
    global baseline_avgs
    print("Scanning section:", scan_section)
    time.sleep(scanTime)  # Delay for scanning

    rfUpdateBaselineValues(scan_section)  # update RF values for every section
    scan_section += 1
    if scan_section > 100:
        scan_section = 0
        iteration_baseline += 1
        if iteration_baseline > 2:
            iteration_baseline = 0
            baseline_avgs = [x / 3 for x in baseline_sums] # calculate averages
            print("Baseline averages calculated:", baseline_avgs)
    
    return scan_section

def rfUpdateBaselineValues(section):
    # Placeholder function to simulate updating RF values for a given section
    print(f"Updating baseline RF values for section {section}")

    # getRFValue(value)  # Example call to get RF value
    test_value = 42  # Placeholder for actual RF value
    baseline_sums[section] += test_value

    # Actual implementation would go here


def scan():
    global scan_section
    global iteration
    global baseline_sums
    print("Scanning section:", scan_section)
    time.sleep(scanTime)  # Delay for scanning

    was_search_mode = rfCompValues(scan_section)  # update RF values for every section

    if was_search_mode:
        print("Going to idle mode")
        baseline_sums = [0.0] * 101  # reset baseline sums
        idlemode.setIdleMode()  # Go back to idle mode af ended search mode
    else:
        scan_section += 1
        if scan_section > 100:
            scan_section = 0
            iteration += 1
            if iteration > 2:
                iteration = 0
                # newbaseline_avgs = [x / 3 for x in newbaseline_sums] # calculate averages
                # print("New baseline averages calculated:", newbaseline_avgs)
                # baseline_avgs = newbaseline_avgs.copy()
                # newbaseline_sums = [0.0] * 100  # reset new baseline sums
    
    return scan_section

def rfCompValues(section):
    global rssi_threshold
    # Placeholder function to simulate updating RF values for a given section
    print(f"Updating RF values for section {section}")

    # getRFValue(value)  # Example call to get RF value

    test_value = 53  # Placeholder for actual RF value
    comp_value = test_value - baseline_avgs[section]
    if comp_value > rssi_threshold:
        searchMode.setSearchMode()
        return True
    else:
        return False  # Example comparison
    
    # Actual implementation would go here