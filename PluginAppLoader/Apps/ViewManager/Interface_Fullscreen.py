# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Set the interface to Fullscreen.
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


def SetInterfaceFullscreen():
    """
    Set the interface to Fullscreen.
    """

    S = InterfaceSettings.InterfaceSettings()

    S.DISPLAY_THRESHOLD = 2.0
    S.SHOW_CURVES = False
    S.SHOW_POINTS = False
    S.ENABLE_MOUSE_FEEDBACK = False

    S.FLAG_ROBODK_TREE_VISIBLE = False
    S.FLAG_ROBODK_REFERENCES_VISIBLE = False
    S.FLAG_ROBODK_LEFT_CLICK = False
    S.FLAG_ROBODK_RIGHT_CLICK = False
    S.FLAG_ROBODK_DOUBLE_CLICK = False

    S.WINDOW_STATE[0] = 5  # Cinema
    S.TOOLBAR_LAYOUT[0] = 0  # Default

    S.Apply()


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SetInterfaceFullscreen()


if __name__ == '__main__':
    runmain()