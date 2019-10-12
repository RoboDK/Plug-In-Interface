# Set the 3D view point from a saved state

# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------

# Import the original module functions
from LoadView import *

if __name__ == "__main__":

    # Define the station parameter name
    VIEW_NAME = "SavedView2"
    LoadView(VIEW_NAME)