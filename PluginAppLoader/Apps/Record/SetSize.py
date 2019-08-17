# This script will promt the user to enter the size of the screen and update the main window of RoboDK accordingly

from robolink import *    # RoboDK API

RDK = Robolink()

newsize = mbox("Set the screen size (size of the 3D window).\nSelect Cancel to set the window back to the default size.", entry="640x480")

RDK.Command("SetSize3D", newsize)
