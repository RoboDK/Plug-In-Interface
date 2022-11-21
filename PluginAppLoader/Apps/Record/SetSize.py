# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Prompt the user to enter the size of the screen and update the main window of RoboDK accordingly.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, roboapps, robodialogs

import Settings


def SetSize(RDK=None, S=None):
    """Prompt the user to enter the size of the screen and update the main window of RoboDK accordingly."""
    if RDK is None:
        RDK = robolink.Robolink()

    if S is None:
        S = Settings.Settings()
        S.Load(RDK)

    # Get the desired screen size from the user
    newsize = robodialogs.InputDialog("Set the screen size (size of the 3D window).\n Width x Height:", S.DEFAULT_SCREEN_SIZE)
    if newsize is None:
        return

    RDK.Command("SetSize3D", f"{newsize[0]}x{newsize[1]}")


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        SetSize()


if __name__ == '__main__':
    runmain()