# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------
from robolink import *

# Start the RoboDK API
RDK = Robolink()

# Ask the user to select an object (no popup will be displayed if the user already selected the object)
selected = RDK.ItemUserPick('Select an object to change the appearance', ITEM_TYPE_OBJECT)

# Check if the user cancelled object selection
if not selected.Valid():    
    exit()

# Display each point as a cube of a given size in mm. 
# Cube size along (x,y,z)
selected.setParam('Display','PARTICLE=CUBE(2,2,2) COLOR=#FF4444FF')
