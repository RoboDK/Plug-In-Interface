# Checkable option example

from robodk import robolink, roboapps
from _AppUtilities import ShowMessage, APP_OPTION_B_KEY
import os

ACTION_NAME = os.path.basename(__file__)


def ActionChecked():
    """Action to perform when the action is checked in RoboDK."""

    RDK = robolink.Robolink()
    RDK.setParam(APP_OPTION_B_KEY, 1.0)
    ShowMessage(RDK, ACTION_NAME, str(RDK.getParam(APP_OPTION_B_KEY)), False)


def ActionUnchecked():
    """Action to perform when the action is unchecked in RoboDK."""

    RDK = robolink.Robolink()
    RDK.setParam(APP_OPTION_B_KEY, 0.0)
    ShowMessage(RDK, ACTION_NAME, str(RDK.getParam(APP_OPTION_B_KEY)), False)


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
        roboapps.KeepChecked()
        ActionChecked()


if __name__ == '__main__':
    runmain()