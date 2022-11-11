# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# Checkable action example.
#
# The main icon for this action is automatically loaded as it shares the same name (ActionCheckable[.py, .svg]).
# The checked icon loaded as it is suffixed with 'Checked'.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import robolink, robomath, roboapps
from _AppUtilities import ShowMessage
import os

ACTION_NAME = os.path.basename(__file__)


def ActionChecked():
    """Action to perform when the action is checked in RoboDK."""

    RDK = robolink.Robolink()
    APP = roboapps.RunApplication()

    ShowMessage(RDK, ACTION_NAME, "Checked! Waiting to be unchecked..", True)

    i = 0
    while APP.Run():
        ShowMessage(RDK, ACTION_NAME, "Checked Status., " + str(i), False)
        robomath.pause(0.25)
        i += 1

    # This will not be called if SkipKill() is not present
    robomath.pause(3)
    ShowMessage(RDK, ACTION_NAME, "Unchecked! This is a post-run message (SkipKill). Closing..", True)


def ActionUnchecked():
    """Action to perform when the action is unchecked in RoboDK."""

    # It is not recommended to use APP.Run() in the Unchecked state!
    RDK = robolink.Robolink()
    ShowMessage(RDK, ACTION_NAME, "Unchecked!", True)
    return


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.

    Example for a 'Checkable Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    Example for a 'Momentary Action':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                roboapps.Exit()  # or sys.exit()
            else:
                roboapps.SkipKill()  # Optional, prevents RoboDK from force-killing the action after 2 seconds
                ActionChecked()

    Example for a 'Checkable Option':

    .. code-block:: python

        def runmain():
            if roboapps.Unchecked():
                ActionUnchecked()
            else:
                roboapps.KeepChecked()  # Important, prevents RoboDK from unchecking the action after it has completed
                ActionChecked()

    """

    if roboapps.Unchecked():
        ActionUnchecked()
    else:
        roboapps.SkipKill()  # Comment this line to have RoboDK kill the process after 2 seconds (if it still runs)
        ActionChecked()


if __name__ == '__main__':
    runmain()