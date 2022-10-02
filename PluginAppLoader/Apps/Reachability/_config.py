#####################################################
## Copyright (C) RoboDK Inc - All Rights Reserved
## Documentation: https://robodk.com/doc/en/RoboDK-API.html
## Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#####################################################

from robodk.roboapps import *
from collections import OrderedDict

FIELDS_UI = OrderedDict()

#------------------------------------------------------------------------
# CONFIGURATION SECTION
APP_NAME = 'Reachability'

# Variable names when displayed on the user interface
# Create this dictionary in the same order that you want to display it
FIELDS_UI = OrderedDict()
#FIELDS_UI['Speed_Approach'] = 'Approach speed (mm/s)'
#FIELDS_UI['Speed_Normal'] = 'Operation Speed (mm/s)'
FIELDS_UI['ShowRobotPoses'] = 'Show Robot'
FIELDS_UI['Unreachable_Timeout'] = 'Unreachable timeout (s)'
FIELDS_UI['Range_TX'] = 'Translation X (m)'
FIELDS_UI['Range_TY'] = 'Translation Y (m)'
FIELDS_UI['Range_TZ'] = 'Translation Z (m)'
FIELDS_UI['Range_RX'] = 'Rotation X (deg)'
FIELDS_UI['Range_RY'] = 'Rotation Y (deg)'
FIELDS_UI['Range_RZ'] = 'Rotation Z (deg)'

# Station name to store
STATIONVAR_NAME = APP_NAME


class Settings(AppSettings):
    """Generic settings class to save and load settings from a RoboDK station and show methods in RoboDK"""
    # List the variable names you would like to save and their default values
    # Important: Try to avoid default None type!!
    # If None is used as default value it will attempt to treat it as a float and None = -1
    # Variables that start with underscore (_) will not be saved
    #Speed_Approach = 200
    #Speed_Normal = 50
    ShowRobotPoses = False
    Unreachable_Timeout = 2
    Range_TX = "[0]"
    Range_TY = "[0]"
    Range_TZ = "[0]"
    Range_RX = "range(-120, 180, 60)"
    Range_RY = "range(-120, 180, 60)"
    Range_RZ = "[0]"

    def __init__(self):
        super(Settings, self).__init__(STATIONVAR_NAME)
        self._FIELDS_UI = FIELDS_UI


if __name__ == "__main__":
    pass
