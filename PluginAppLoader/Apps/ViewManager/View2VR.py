# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Set the current view in the RoboDK main window to the VR headset.
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


def View2VR(RDK=None):
    """
    Set the current view in the RoboDK main window to the VR headset.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    vp = RDK.ViewPose()

    result = RDK.Command("VR")  # open the VR view

    strpose = str(robomath.Pose_2_TxyzRxyz(robomath.transl(0, 0, +2000) * vp))[1:-1]
    result = RDK.Command("ViewPoseVR", strpose)
    print(strpose)

    if result != "OK":
        RDK.ShowMessage("Problems setting VR view: " + result, False)
        return

    RDK.ShowMessage("Window view sent to VR headset", False)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        View2VR()


if __name__ == '__main__':
    runmain()