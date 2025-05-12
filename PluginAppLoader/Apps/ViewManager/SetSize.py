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


def SetSize(RDK=None):
    """
    Prompt the user to enter the size of the screen and update the main window of RoboDK accordingly.
    """
    if RDK is None:
        RDK = robolink.Robolink()

    # Get the desired screen size from the user
    entry = [1920, 1080]

    # If available, use the current size
    current_size = RDK.Command('SetSize3D')
    if len(current_size.split('x', maxsplit=2)) == 2:
        entry = current_size.split('x')

    newsize = robodialogs.InputDialog("Set the screen size (size of the 3D window).\nEnter ' ' to unlock the screen\nWidth x Height:", value=entry)
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