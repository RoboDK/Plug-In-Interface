# This script will promt the user to enter the size of the screen and update the main window of RoboDK accordingly

from robodk.robolink import *  # RoboDK API
from robodk.robodialogs import mbox


def runmain():
    RDK = Robolink()
    newsize = mbox("Set the screen size (size of the 3D window).\nSelect Cancel to set the window back to the default size.", entry="960x720")
    RDK.Command("SetSize3D", newsize)


# Function to run when this module is executed on its own or by selecting the action button in RoboDK
if __name__ == "__main__":
    runmain()
