# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Show targets from selected program(s) and hide all others.
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


def ShowProgramTargets():
    """Show targets from selected program(s) and hide all others."""
    RDK = robolink.Robolink()

    programs = [x for x in RDK.Selection() if x.Type() == robolink.ITEM_TYPE_PROGRAM]
    if not programs:
        return

    show_targets = []
    for program in programs:
        show_targets.extend(utils.getProgramTargets(program))

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
        ShowProgramTargets()


if __name__ == '__main__':
    runmain()
