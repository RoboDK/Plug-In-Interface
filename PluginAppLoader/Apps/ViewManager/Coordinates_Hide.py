from robodk.robolink import *

# Start RoboDK Skipping default Initialization settings and default tree (second parameter is redundant with the first)
#RDK = Robolink(args=["-SKIPINI", "-TREE_STATE=0"])
RDK = Robolink()

RDK.Command("ShowCoords", "0")  # Detached and hidden
