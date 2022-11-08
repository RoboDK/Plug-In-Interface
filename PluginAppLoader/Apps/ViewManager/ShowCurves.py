# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Show/hide the text in the 3D view.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, roboapps


def ActionChecked():
    """Hide the text in the 3D view."""

    RDK = robolink.Robolink()
    RDK.Command("DisplayCurves", 0)


def ActionUnchecked():
    """Show the text in the 3D view."""

    RDK = robolink.Robolink()
    RDK.Command("DisplayCurves", 1)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        ActionUnchecked()
    else:
        roboapps.KeepChecked()
        ActionChecked()


if __name__ == '__main__':
    runmain()