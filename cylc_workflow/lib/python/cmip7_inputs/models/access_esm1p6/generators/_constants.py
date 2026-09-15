""" This contains all the common constants for generating the ESM1.5 ancil files. """

from datetime import datetime

ANCIL_TODAY = datetime.now().strftime("%Y.%m.%d")
REAL_MISSING_DATA_INDICATOR = -32768 * 32768.0

CMIP7_PI_YEAR = 1850

CMIP7_HI_BEG_YEAR = CMIP7_PI_YEAR
# Model time interpolation requires an extra year
CMIP7_HI_END_YEAR = 2023