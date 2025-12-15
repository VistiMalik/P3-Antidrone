import time

# Global variable to keep track of the current scan section
scanSection = 1
iterationBaseline = 1
iteration = 1
baselineSums = [0.0] * 100  # Baseline sums for 100 sections
baselineAvgs = []   # Baseline averages for the 100 sections
# newBaselineSums = [0.0] * 100  # New baseline sums for 100 sections
# newBaselineAvgs = []   # New baseline averages for the 100 sections

# Function to scan for every section and iterate through sections
def scanBaseline():
    global scanSection
    global iterationBaseline
    print("Scanning section:", scanSection)
    time.sleep(0.05)  # simulate delay for scanning

    rfUpdateBaselineValues(scanSection)  # update RF values for every section
    scanSection += 1
    if scanSection > 100:
        scanSection = 1
        iterationBaseline += 1
        if iterationBaseline > 3:
            iterationBaseline = 1
            baselineAvgs = [x / 3 for x in baselineSums] # calculate averages
            print("Baseline averages calculated:", baselineAvgs)
    
    return scanSection

def rfUpdateBaselineValues(section):
    # Placeholder function to simulate updating RF values for a given section
    print(f"Updating baseline RF values for section {section}")

    # getRFValue(value)  # Example call to get RF value
    testValue = 42  # Placeholder for actual RF value
    baselineSums[section - 1] += testValue

    # Actual implementation would go here


def scan():
    global scanSection
    global iteration
    print("Scanning section:", scanSection)
    time.sleep(0.05)  # simulate delay for scanning

    rfCompValues(scanSection)  # update RF values for every section
    scanSection += 1
    if scanSection > 100:
        scanSection = 1
        iteration += 1
        if iteration > 3:
            iteration = 1
            # newBaselineAvgs = [x / 3 for x in newBaselineSums] # calculate averages
            # print("New baseline averages calculated:", newBaselineAvgs)
            # baselineAvgs = newBaselineAvgs.copy()
            # newBaselineSums = [0.0] * 100  # reset new baseline sums
    
    return scanSection

def rfCompValues(section):
    # Placeholder function to simulate updating RF values for a given section
    print(f"Updating RF values for section {section}")

    testValue = 21  # Placeholder for actual RF value
    # Actual implementation would go here