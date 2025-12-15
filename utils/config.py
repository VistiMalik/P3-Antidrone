# Module for configuration constants for the antidrone system

# RSSI threshold for entering search mode:
rssi_threshold = 10  # RSSI threshold for drone detection (test value)

# Movement speed settings:
speedSetup = 0.001  # Move speed during setup phase
speedIdle = 0.0005  # Move speed during idle state
speedSearch = 0.0001  # Move speed during search operations

# Scan time:
scanTime = 0.05  # Time duration for scanning in seconds (Halts movement during scan)

# GPIO pin assignments:
PULL_H = 4
PULL_V = 22
DIR_H = 17
DIR_V = 25