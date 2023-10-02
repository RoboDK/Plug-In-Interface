# --------------------------------------------
# --------------- DESCRIPTION ----------------
#
# This file lets you edit the settings of this RoboDK App.
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
    """Surface Pattern Generator App Settings."""

    def __init__(self, settings_param='Surface-Pattern-Generator-Settings'):
        super().__init__(settings_param)

        from collections import OrderedDict
        self._FIELDS_UI = OrderedDict()

        # --------------------------------------------
        self._FIELDS_UI['SECTION_PATTERN'] = "$PATTERN$"
        self._FIELDS_UI['SIZE_X'] = "Size along X (mm)"
        self._FIELDS_UI['SIZE_Y'] = "Size along Y (mm)"
        self.SIZE_X = 500.0
        self.SIZE_Y = 500.0

        self._FIELDS_UI['STEP_X'] = "Step along X (mm)"
        self._FIELDS_UI['STEP_Y'] = "Step along Y (mm)"
        self.STEP_X = 20.0
        self.STEP_Y = 50.0

        self._FIELDS_UI['ANGLE_TRIANGLE'] = "Triangular path (deg)"
        self.ANGLE_TRIANGLE = 0.0

        self._FIELDS_UI['COVER_ALL'] = "Cover all surface"
        self._FIELDS_UI['EVEN_DISTRIBUTION'] = "Distribute lines evenly"
        self._FIELDS_UI['CONTINUOUS'] = "Connect lines"
        self.COVER_ALL = False
        self.EVEN_DISTRIBUTION = False
        self.CONTINUOUS = True

        self._FIELDS_UI['REMOVE_UNPROJECTED_POINTS'] = "Remove points that are not on the surface"
        self.REMOVE_UNPROJECTED_POINTS = False

        self._FIELDS_UI['REPEAT_TIMES'] = "Repeat times"
        self._FIELDS_UI['REPEAT_OFFSET'] = "Repeat Offset along Z (mm)"
        self.REPEAT_TIMES = 1
        self.REPEAT_OFFSET = 2.0

        self._FIELDS_UI['SECTION_PROGRAM'] = "$PROGRAM$"
        self._FIELDS_UI['CREATE_PROGRAM'] = "Create Program"
        self._FIELDS_UI['ANGLE_TCP_X'] = "Tool angle X (deg)"
        self._FIELDS_UI['ANGLE_TCP_Y'] = "Tool angle Y (deg)"
        self.CREATE_PROGRAM = True
        self.ANGLE_TCP_X = 0.0
        self.ANGLE_TCP_Y = 0.0

        self._FIELDS_UI['SPEED_OPERATION'] = "Operation speed (mm/s)"
        self.SPEED_OPERATION = 20.0


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
        S.ShowUI('Surface Pattern Generator Settings')


if __name__ == '__main__':
    runmain()