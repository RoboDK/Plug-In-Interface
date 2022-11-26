# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file let's you edit the settings of this RoboDK App.
#
# More information about the RoboDK API for Python here:
#     https://robodk.com/doc/en/RoboDK-API.html
#     https://robodk.com/doc/en/PythonAPI/index.html
#
# More information on RoboDK Apps here:
#     https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginAppLoader
#
# --------------------------------------------

from robodk import roboapps


class Settings(roboapps.AppSettings):
    """Game Controller's App Settings"""

    def __init__(self, settings_param='Game-Controller-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        self._FIELDS_UI['RUN_ON_ROBOT'] = "Run on connected robot"
        self.RUN_ON_ROBOT = True

        # Robot speeds
        self._FIELDS_UI['MAX_LINEAR_SPEED'] = "Maximum linear speed [mm/s]"
        self._FIELDS_UI['MAX_JOINT_SPEED'] = "Maximum joint speed [deg/s]"
        self.MAX_LINEAR_SPEED = 25.0  # mm/s
        self.MAX_JOINT_SPEED = 20.0  # deg/s

        # Linear move
        self._FIELDS_UI['LINEAR_STEPS_MAX'] = "Maximum linear step size [mm/step]"
        self._FIELDS_UI['LINEAR_STEPS_MIN'] = "Minimum linear step size [mm/step]"
        self._FIELDS_UI['LINEAR_STEPS_INIT'] = "Default linear step size [mm/step]"
        self.LINEAR_STEPS_MAX = 50  # mm/step
        self.LINEAR_STEPS_MIN = 0.5  # mm/step
        self.LINEAR_STEPS_INIT = 10  # mm/step

        # Angular move
        self._FIELDS_UI['ANGULAR_STEPS_MAX'] = "Maximum angular step size [deg/step]"
        self._FIELDS_UI['ANGULAR_STEPS_MIN'] = "Minimum angular step size [deg/step]"
        self._FIELDS_UI['ANGULAR_STEPS_INIT'] = "Default angular step size [deg/step]"
        self.ANGULAR_STEPS_MAX = 30  # deg/step
        self.ANGULAR_STEPS_MIN = 1  # deg/step
        self.ANGULAR_STEPS_INIT = 5  # deg/step

        # Steps
        self._FIELDS_UI['STEPS_INC_FACTOR'] = "Step increase/decrease factor [%/100]"
        self.STEPS_INC_FACTOR = 0.25  # % of step increase/decrease


def runmain():
    """
    Entrypoint of this action when it is executed on its own or interacted with in RoboDK.
    Important: Use the function name 'runmain()' if you want to compile this action.
    """

    if roboapps.Unchecked():
        roboapps.Exit()
    else:
        S = Settings()
        S.Load()
        S.ShowUI('Game Controller Settings')


if __name__ == '__main__':
    runmain()