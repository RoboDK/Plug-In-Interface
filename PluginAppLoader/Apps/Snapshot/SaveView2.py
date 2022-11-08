# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Save the 3D view point as a station parameter, as specified by the user.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import roboapps, robodialogs

from SaveView import SaveView


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        id = robodialogs.mbox("View ID", entry=0)
        if id == False:
            roboapps.Exit()  # User cancel
        SaveView('Snapshot-View-' + str(id).strip())


if __name__ == '__main__':
    runmain()