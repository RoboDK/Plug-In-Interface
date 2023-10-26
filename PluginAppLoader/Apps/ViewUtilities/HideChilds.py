# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Hide (set invisible) all children of the selected items.
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
    Hide (set invisible) all children of the selected items.
    """
    RDK = robolink.Robolink()

    selection = RDK.Selection()
    if not selection:
        return

    RDK.Render(False)

    # for item in selection:
    #     item.setParam('VisibleChilds', 0)  # RoboDK 5.6.7

    def recurse(item):
        for child in item.Childs():
            child.setVisible(False)
            recurse(child)

    for item in selection:
        recurse(item)

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
