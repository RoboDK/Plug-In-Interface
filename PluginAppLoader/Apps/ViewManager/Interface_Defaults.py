# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Set the interface to default.
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

import InterfaceSettings


def SetInterfaceDefault():
    """
    Set the interface to default.
    """

    # Default settings of InterfaceSettings are the expected defaults
    S = InterfaceSettings.InterfaceSettings()
    S.Apply()


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SetInterfaceDefault()


if __name__ == '__main__':
    runmain()