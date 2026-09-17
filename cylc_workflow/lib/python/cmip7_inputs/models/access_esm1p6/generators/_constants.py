""" This contains all the common constants for generating the ESM1.5 ancil files. """

from datetime import datetime

ANCIL_TODAY = datetime.now().strftime("%Y.%m.%d")
REAL_MISSING_DATA_INDICATOR = -32768 * 32768.0
<<<<<<< HEAD
MONTHS_IN_A_YEAR = 12
=======
MONTHS_IN_A_YEAR = 12


# Start year for picontrol experiment
PI_START_YEAR = 1850
DAYS_IN_PI_YEAR = 365.0

# Start year for historical experiment
HI_START_YEAR = PI_START_YEAR
# Model time interpolation requires an extra year
HI_END_YEAR = 2023

#===============================
# solar constants
#===============================

SOLAR_ARRAY_START_YEAR = 1700
SOLAR_ARRAY_END_YEAR = 2300
SOLAR_PI_DEFAULT_YEARLY_MEAN = 1361.603

#===============================
# volcanic constants
#===============================

# TODO: Are these the same as the cmip7_HI_BEG_YEAR and cmip7_HI_END_YEAR? If so, we should use those instead of duplicating the values here.
HI_VOLCANIC_START_YEAR = 1850
HI_VOLCANIC_END_YEAR = 2023

NBR_OF_BANDS = 4
NBR_TAPER_YEARS = 10
SAOD_START_YEAR = 1850
SAOD_END_YEAR = 2300
# The prescribed wavelength for stratospheric aerosol optical depth
SAOD_WAVELENGTH = 550.0 * 1e-9
# Scaling ratio to use with calculated SAOD
SAOD_SCALING = 10000.0
>>>>>>> 846bfef (Add volcanic before testing)
