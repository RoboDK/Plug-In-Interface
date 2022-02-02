#-------------------------------------------------------
# This file provides generic tools for your Python app in RoboDK
# This file includes:
#   1. RunApplication: class to cleanly stop checkable actions (checkable actions get the Terminate/SIGINT signal when they are unchecked)
#   2. App utility functions: simple way to detect an unchecked action from RoboDK by capturing the Terminate signal
#-------------------------------------------------------

import os
import sys
import time
from robodk import robolink


class RunApplication:
    """Class to detect when the terminate signal is emited to stop an action.

    .. code-block:: python

        run = RunApplication()
        while run.Run():
            # your main loop to run until the terminate signal is detected
            ...

    """
    time_last = -1
    param_name = None
    RDK = None

    def __init__(self, rdk=None):
        if rdk is None:
            self.RDK = robolink.Robolink()
        else:
            self.RDK = rdk

        self.time_last = time.time()
        if len(sys.argv) > 0:
            path = sys.argv[0]
            folder = os.path.basename(os.path.dirname(path))
            file = os.path.basename(path)
            if file.endswith(".py"):
                file = file[:-3]
            elif file.endswith(".exe"):
                file = file[:-4]

            self.param_name = file + "_" + folder
            self.RDK.setParam(self.param_name, "1")  # makes sure we can run the file separately in debug mode

    def Run(self):
        time_now = time.time()
        if time_now - self.time_last < 0.1:
            return True
        self.time_last = time_now
        if self.param_name is None:
            # Unknown start
            return True

        keep_running = not (self.RDK.getParam(self.param_name) == 0)
        return keep_running


def Unchecked():
    """Verify if the command "Unchecked" is present. In this case it means the action was just unchecked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Unchecked" in sys.argv[1:]:
            return True

    return False


def Checked():
    """Verify if the command "Checked" is present. In this case it means the action was just checked from RoboDK (applicable to checkable actions only)."""
    if len(sys.argv) >= 2:
        if "Checked" in sys.argv[1:]:
            return True

    return False


def KeepChecked():
    """Keep an action checked even if the execution of the script completed (this is applicable to Checkable actions only)"""
    print("App Setting: Keep checked")
    sys.stdout.flush()


def SkipKill():
    """For Checkable actions, this setting will tell RoboDK App loader to not kill the process a few seconds after the terminate function is called.
    This is needed if we want the user input to save the file. For example: The Record action from the Record App."""
    print("App Setting: Skip kill")
    sys.stdout.flush()


def runmain():
    pass


if __name__ == "__main__":
    runmain()
