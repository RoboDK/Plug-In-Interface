# This script shows how to save the current view point as a station parameter

# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------

# Import the original module functions
from SaveView import *

if __name__ == "__main__":

    # Define the station parameter name
    VIEW_NAME = "SavedView2"
    SaveView(VIEW_NAME)