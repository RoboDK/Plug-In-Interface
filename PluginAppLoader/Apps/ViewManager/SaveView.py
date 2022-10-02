# This script shows how to save the current view point as a station parameter

# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------

from robodk.robolink import *
from robodk.robomath import Pose_2_KUKA


def SaveView(view_name):

    # Start the RoboDK API
    RDK = Robolink()

    # Get the 3D view pose
    vp = RDK.ViewPose()

    # Convert to a string as XYZABC
    vp_str = str(Pose_2_KUKA(vp))

    # Save it as a station parameter (saved with the RDK file)
    RDK.setParam(view_name, vp_str)

    RDK.ShowMessage("Current view point saved: " + vp_str, False)
    print("Done")


if __name__ == "__main__":
    # Define the station parameter name
    VIEW_NAME = "SavedView"
    SaveView(VIEW_NAME)