# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Stop all programs and moving robots in the station.
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


def StopProgramsAndRobots():
    """
    Stop all programs and moving robots in the station.
    """

    RDK = robolink.Robolink()

    RDK.Render(False)

    programs = RDK.ItemList(robolink.ITEM_TYPE_PROGRAM)
    robots = RDK.ItemList(robolink.ITEM_TYPE_ROBOT)

    for item in robots + programs:
        item.Stop()

    RDK.Render(True)


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        StopProgramsAndRobots()


if __name__ == '__main__':
    runmain()