# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Show (set visible) the selected items, and hide (set invisible) all other items.
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


def ShowOnlySelection():
    """
    Show (set visible) the selected items, and hide (set invisible) all other items.
    """
    RDK = robolink.Robolink()

    selection = RDK.Selection()
    if not selection:
        return

    RDK.Render(False)

    for item in RDK.ItemList():
        if item in selection:
            item.setVisible(True)
        else:
            item.setVisible(False)

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ShowOnlySelection()


if __name__ == '__main__':
    runmain()
