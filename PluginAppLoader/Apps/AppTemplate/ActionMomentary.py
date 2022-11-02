# Momentary action example
from robodk import robolink, roboapps
from _AppUtilities import ShowMessage
import os

ACTION_NAME = os.path.basename(__file__)


def ActionMomentary():
    """Action to perform when the action is clicked in RoboDK."""

    RDK = robolink.Robolink()
    ShowMessage(RDK, ACTION_NAME, "Clicked!", True)


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
        roboapps.Exit()
    else:
        ActionMomentary()


if __name__ == '__main__':
    runmain()