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

# Display points as simple dots given a certain size (suitable for fast rendering)
# Color is defined as AARRGGBB. It can also be a named color
selected.setParam('Display', 'POINTSIZE=4 COLOR=#FF771111')

