# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Collapse the selected items and their children in the tree.
# This also collapse (hide instructions) of programs.
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


def TreeCollapse():
    """
    Collapse the selected items and their children in the tree.
    This also collapse (hide instructions) of programs.
    """
    RDK = robolink.Robolink()

    selection = RDK.Selection()
    if not selection:
        return

    RDK.Render(False)

    def recurse(item):
        for child in item.Childs():
            utils.collapse(child)
            recurse(child)

    for item in selection:
        utils.collapse(item)
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
        TreeCollapse()


if __name__ == '__main__':
    runmain()
