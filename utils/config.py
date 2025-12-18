# Module for configuration constants for the antidrone system

# IP and Port settings:
IP = "172.20.10.2"  # IP address of the Raspberry Pi

# RSSI threshold for entering search mode:
rssi_threshold = 100  # RSSI threshold for drone detection (test value)

# Movement speed settings:
speedSetup = 0.00008  # Move speed during setup phase
speedIdle = 0.00004  # Move speed during idle state
speedSearch = 0.00002  # Move speed during search operations

# Scan time:
scanTime = 0.05  # Time duration for scanning in seconds (Halts movement during scan)

# Coordinate settings:
vert_start_pos = 0  # Starting vertical position in degrees
horz_start_pos = 0  # Starting horizontal position in degrees
# Vertical movement limits:
vert_min = 0  # Minimum vertical position in degrees
vert_max = 90  # Maximum vertical position in degrees

GEAR_RATIO = 3  # Gear ratio for vertical motor

# GPIO pin assignments:
PULL_H = 4
PULL_V = 22
DIR_H = 17
DIR_V = 10

latitude = 0.0  # Placeholder for latitude
longitude = 0.0  # Placeholder for longitude

setup_sweep_count = 3  # Number of setup sweeps to establish baseline

channels = [2445]  # Frequencies in MHz to scan for drones