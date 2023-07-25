# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Show (set visible) every item in the station.
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
import _Utilities as utils


def ShowAll():
    """
    Show (set visible) every item in the station.
    """
    RDK = robolink.Robolink()

    RDK.Render(False)

    for item in RDK.ItemList():
        item.setVisible(True)

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ShowAll()


if __name__ == '__main__':
    runmain()
