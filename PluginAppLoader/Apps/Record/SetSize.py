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
        S.Load()

    # Get the desired screen size from the user
    w, h = S.DEFAULT_SCREEN_SIZE
    newsize = robodialogs.mbox("Set the screen size (size of the 3D window).\n Width x Height:", entry=f"{w}x{h}")
    if newsize == False:
        return

    RDK.Command("SetSize3D", newsize)


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