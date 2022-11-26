# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file adds the Object Deleter (loop) script to your RoboDK station.
# You can then call it programmatically from a RoboDK program call.
# To use the zone ID #2, call DeleteObjectsLoop(2).
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
import os


def AddDeleteObjectsLoopScript():
    """
    This file adds the Object Deleter script to your RoboDK station.
    You can then call it programmatically from a RoboDK program call.
    To use the zone ID #2, call DeleteObjectsLoop(2).
    """

    RDK = robolink.Robolink()
    script = RDK.AddFile(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/DeleteObjectsLoop.py'))
    script.setName('DeleteObjectsLoop')


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        AddDeleteObjectsLoopScript()


if __name__ == '__main__':
    runmain()