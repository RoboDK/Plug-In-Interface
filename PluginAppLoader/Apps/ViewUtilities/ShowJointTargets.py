# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Show all joint targets and hide cartesian targets in the station.
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


def ShowJointTargets():
    """Show all joint targets and hide cartesian targets in the station."""
    RDK = robolink.Robolink()

    show_targets = utils.getJointTargets(RDK)
    all_targets = utils.getTargets(RDK)
    if all_targets:
        RDK.Render(False)
        for target in all_targets:
            if target in show_targets:
                target.setVisible(True)
            else:
                target.setVisible(False)
        RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        ShowJointTargets()


if __name__ == '__main__':
    runmain()
