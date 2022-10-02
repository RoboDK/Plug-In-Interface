# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------
from robodk.robolink import *

# Start the RoboDK API
RDK = Robolink()

# Ask the user to select an object (no popup will be displayed if the user already selected the object)
selected = RDK.ItemUserPick('Select an object to change the appearance', ITEM_TYPE_OBJECT)

# Check if the user cancelled object selection
if not selected.Valid():
    exit()

# Example to change the curve colors
# Set to Orange color (255, 127, 0)
selected.setColorCurve([1, 0.5, 0, 1])

# Change the size of displayed curves:
selected.setParam('Display', 'LINEW=3')
