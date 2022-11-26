# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Expand the selected items and their children in the tree.
# This also expand (show instructions) of programs.
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


def TreeExpand():
    """
    Expand the selected items and their children in the tree.
    This also expand (show instructions) of programs.
    """
    RDK = robolink.Robolink()

    selection = RDK.Selection()
    if not selection:
        return

    RDK.Render(False)

    def recurse(item):
        for child in item.Childs():
            utils.expand(child)
            recurse(child)

    for item in selection:
        utils.expand(item)
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
        TreeExpand()


if __name__ == '__main__':
    runmain()
