# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Save the 3D view point as a station parameter.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, roboapps


def SaveView(view_name):
    """
    Save the 3D view point as a station parameter.
    """

    # Start the RoboDK API
    RDK = robolink.Robolink()

    # Get the 3D view pose
    vp = RDK.ViewPose()

    # Convert to a string as XYZABC
    vp_str = str(robomath.Pose_2_KUKA(vp))

    # Save it as a station parameter (saved with the RDK file)
    RDK.setParam(view_name, vp_str)

    RDK.ShowMessage("Current view point saved: " + vp_str, False)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SaveView("Snapshot-View-0")


if __name__ == '__main__':
    runmain()