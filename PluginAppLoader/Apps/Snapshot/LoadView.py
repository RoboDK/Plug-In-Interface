# Set the 3D view point from a saved state

# For more information about the RoboDK API:
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
#-------------------------------------------------------

from robodk.robolink import *
from robodk.robomath import KUKA_2_Pose


def LoadView(view_name):
    import ast

    # Start the RoboDK API
    RDK = Robolink()

    vp_str = RDK.getParam(view_name)
    if vp_str is None:
        RDK.ShowMessage("Preferred view not recorded. Save a view point first", False)
        quit()

    # Lazy way to convert a list as a string to a list of floats
    #exec('vp_xyzabc = ' + vp_str, locals())
    vp_xyzabc = ast.literal_eval(vp_str)

    vp = KUKA_2_Pose(vp_xyzabc)
    RDK.setViewPose(vp)

    print("Done")


if __name__ == "__main__":
    # Define the station parameter name
    VIEW_NAME = "SavedView"
    LoadView(VIEW_NAME)