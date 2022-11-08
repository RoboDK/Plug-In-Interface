# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Restore the 3D view point from a saved station parameter.
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
import ast


def LoadView(view_name):
    """
    Restore the 3D view point from a saved station parameter.
    """

    # Start the RoboDK API
    RDK = robolink.Robolink()

    vp_str = RDK.getParam(view_name)
    if vp_str is None:
        RDK.ShowMessage(f"View \"{view_name}\" not recorded. Save a view point first", False)
        return

    # Lazy way to convert a list as a string to a list of floats
    vp_xyzabc = ast.literal_eval(vp_str)

    vp = robomath.KUKA_2_Pose(vp_xyzabc)
    RDK.setViewPose(vp)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        LoadView("Snapshot-View-0")


if __name__ == '__main__':
    runmain()