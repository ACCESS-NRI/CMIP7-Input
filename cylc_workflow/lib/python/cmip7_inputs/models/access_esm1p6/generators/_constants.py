""" This contains all the common constants for generating the ESM1.5 ancil files. """

from datetime import datetime

TODAY = datetime.now().strftime("%Y.%m.%d")
REAL_MISSING_DATA_INDICATOR = -32768 * 32768.0

# Start year for picontrol experiment
PI_START_YEAR = 1850

# Start year for historical experiment
HI_START_YEAR = PI_START_YEAR
# Model time interpolation requires an extra year
HI_END_YEAR = 2023