"""Physical constants, model versions, and formatting tokens for CMIP7
ancillary
generation.
"""

from datetime import datetime

ANCIL_TODAY = datetime.now().strftime("%Y.%m.%d")
REAL_MISSING_DATA_INDICATOR = -32768 * 32768.0
MONTHS_IN_A_YEAR = 12
UM_VERSION = "7.3"
