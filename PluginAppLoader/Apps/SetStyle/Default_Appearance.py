# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------
from robodk.robolink import *

# Start the RoboDK API
RDK = Robolink()

# Ask the user to select an object (no popup will be displayed if the user already selected the object)
selected = RDK.ItemUserPick('Select an object', ITEM_TYPE_OBJECT)

# Check if the user cancelled object selection
if not selected.Valid():    
    exit()

# Reset apprearance (default point color)
# This applies to points only
selected.setParam('Display', '')

