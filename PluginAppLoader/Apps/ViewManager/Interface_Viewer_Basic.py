from robodk.robolink import *
RDK = Robolink()

# Improve render speed for VR: Do not display objects smaller than 1% of the screen 
RDK.Command("DisplayThreshold", 2)

RDK.Command("MouseFeedback", 0) # Remove mouse feedback
RDK.Command("DisplayCurves", 0) # Hide Curves
RDK.Command("DisplayPoints", 0) # Hide Points

# Allow all default RoboDK flags
# https://robodk.com/doc/en/PythonAPI/robodk.html#robodk.robolink.Robolink.setFlagsRoboDK
block_flags = 0

#block_flags = block_flags and FLAG_ROBODK_TREE_ACTIVE 
block_flags = block_flags | FLAG_ROBODK_TREE_VISIBLE # Hide the tree
block_flags = block_flags | FLAG_ROBODK_REFERENCES_VISIBLE  # Hide the coordinate systems

# block_flags = block_flags | FLAG_ROBODK_MENU_ACTIVE # Hide the menu

block_flags = block_flags | FLAG_ROBODK_LEFT_CLICK  # Prevent left click 
block_flags = block_flags | FLAG_ROBODK_RIGHT_CLICK # Prevent right click
block_flags = block_flags | FLAG_ROBODK_DOUBLE_CLICK # Prevent double click

# Update RoboDK flags
RDK.setFlagsRoboDK(FLAG_ROBODK_ALL & ~block_flags)




RDK.setWindowState(WINDOWSTATE_NORMAL)
RDK.Command("ToolbarLayout", "Viewer")
RDK.setWindowState(WINDOWSTATE_MAXIMIZED)

#RDK.setWindowState(WINDOWSTATE_CINEMA)



