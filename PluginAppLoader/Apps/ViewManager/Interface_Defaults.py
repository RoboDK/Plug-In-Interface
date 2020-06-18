from robolink import *
RDK = Robolink()

RDK.Command("DisplayThreshold", 0.1) # Display everything

RDK.Command("DisplayCurves", 0) # Hide Curves
RDK.Command("DisplayPoints", 0) # Hide Points

# Remove mouse feedback (may slow down VR headset if playing with the cell)
RDK.Command("MouseFeedback", 1)


# Allow all default RoboDK flags
# https://robodk.com/doc/en/PythonAPI/robolink.html#robolink.Robolink.setFlagsRoboDK
RDK.setFlagsRoboDK(FLAG_ROBODK_ALL)


RDK.setWindowState(WINDOWSTATE_NORMAL)
#RDK.Command("ToolbarLayout", "Default") # already done with the previous command
RDK.setWindowState(WINDOWSTATE_MAXIMIZED)
#RDK.setWindowState(WINDOWSTATE_CINEMA)

